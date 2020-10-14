import json
import requests_html as req
import webbrowser
import io
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk

import urls_and_selectors as us

#TODO Learn about ttk Styles
#TODO Display news summary as TopLevel window

class MainWindow(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.style = ttk.Style()

        # Search_company shortcut
        self.search_comp = ttk.Entry(self)
        self.search_comp.grid(row=0, column=0)
        self.search_comp.bind('<KeyRelease>', lambda e: self.search_suggestions(self.search_comp.get()))

        self.search_button = ttk.Button(self, text='Search', command=lambda: 
                                                            [self.ticker_info_window(),
                                                             self.search_comp.delete(0, len(self.search_comp.get()))])
        self.search_button.grid(row=0, column=1)

        # Creating a new window to show search_suggestions
        self.suggs_window = tk.Toplevel(self)
        self.suggs_window.withdraw()

        self.stock_news()

    # Function to be used in ticker_info_window
    def stock_data(self, symbol):
        
        session = req.HTMLSession()

        if symbol[0] == '^':
            # Modified symbol variable without '^'
            mod_symbol = symbol.replace('^', '')
            r = session.get(f'https://finance.yahoo.com/quote/%5E{mod_symbol}?p={symbol}')
        else:
            r = session.get(f'https://finance.yahoo.com/quote/{symbol}?p={symbol}')
        
        company_name = r.html.xpath(us.company_name, first=True).text
        stock_value = r.html.xpath(us.stock_value, first=True).text
        value_change = r.html.xpath(us.value_change, first=True).text

        quote_summary = r.html.xpath(us.summary, first=True)
        summary_list = quote_summary.text.split('\n')
        
        if len(summary_list) > 32:
            summary_list = quote_summary.text.split('\n')[0:32]
        
        summary_keys = summary_list[0:len(summary_list):2]
        summary_values = summary_list[1:len(summary_list):2]

        summary = dict(zip(summary_keys, summary_values))

        return company_name, stock_value, value_change, summary

    # Displaying data retrieved from stock_data
    def ticker_info_window(self):
        #TODO create ticker_info_window
        name, value, value_change, summary = self.stock_data(self.search_comp.get())

        name_label = ttk.Label(self, text=name)
        value_label = ttk.Label(self, text=value)
        value_change_label = ttk.Label(self, text=value_change)

        name_label.grid(row=1, column=0 ,columnspan=4, sticky='w')
        value_label.grid(row=2, column=0, columnspan=2, sticky='e')
        value_change_label.grid(row=2, column=2, columnspan=2, sticky='w')

        row = 3
        for k,v in summary.items():
            ttk.Label(self, text=k).grid(row=row, column=0)
            ttk.Label(self, text=v).grid(row=row, column=1)
            row += 1

    def search_suggestions(self, symbol):

        for child in self.suggs_window.winfo_children():
            child.destroy()

        url = (f'https://query1.finance.yahoo.com/v1/finance/search?q={symbol}&lang=en-'
              'US&region=US&quotesCount=6&newsCount=4&enableFuzzyQuery=false&'
              'quotesQueryId=tss_match_phrase_query&multiQuoteQueryId=multi_'
              'quote_single_token_query&newsQueryId=news_cie_vespa&enableCb='
              'true&enableNavLinks=true&enableEnhancedTrivialQuery=true')

        session = req.HTMLSession()
        res = session.get(url)
        page_text = json.loads(res.html.text)

        # Getting rid of KeyError
        try:
            suggestions = page_text['quotes']
        except KeyError:
            suggestions = []

        suggestions = [item for item in suggestions if item['isYahooFinance'] == True]

        # Dynamically creating labels to display search suggestions
        n = 0
        for item in suggestions:
            # If ticker name is too long, shorten it
            if len(item['symbol']) > 8:
                ticker = item['symbol'][0:8] + '...'
            else:
                ticker = item['symbol'] 

            ttk.Label(self.suggs_window, text=ticker).grid(row=n, column=0)
            n += 1

        self.suggs_window.deiconify()
        self.search_comp.focus_set()
        
        # If search bar is empty, hide window
        if suggestions == []:
            self.suggs_window.withdraw()

    def stock_news(self):
         
        url = us.investing_news
        session = req.HTMLSession()
        r = session.get(url)

        headlines = []
        news_urls = []
        images = []
        for n in range(1, 13):
            try:
                headlines.append(r.html.xpath(f'//*[@id="leftColumn"]/div[4]/article[{n}]/div[1]/a', first=True).text)
                news_urls.append(r.html.xpath(f'//*[@id="leftColumn"]/div[4]/article[{n}]/div[1]/a', first=True).absolute_links.pop())
                images.append(r.html.xpath(f'//*[@id="leftColumn"]/div[4]/article[{n}]/a/img', first=True).attrs['data-src'])
            except AttributeError:
                headlines.append('NoneTypeObject')
                news_urls.append('NoneTypeObject')
                images.append('NoneTypeObject')

        headlines = [item for item in headlines if item != 'NoneTypeObject']
        news_urls = [item for item in news_urls if item != 'NoneTypeObject']
        images_src = [item for item in images if item != 'NoneTypeObject']
               
        images = []
        for img_src in images_src:
            # turning a bytes representation of an image(which we web scraped from the site) into a format usable by ImageTk.PhotoImage  
            images.append(Image.open(io.BytesIO(session.get(img_src).content)))

        # images to be used in tk widgets
        tk_images = []
        for img in images:
            tk_images.append(ImageTk.PhotoImage(img))
            
        news0 = ttk.Label(self, text=headlines[0], image=tk_images[0], compound='right')
        news0.image = tk_images[0]
        news0.grid(row=1, column=0)
        news0.bind('<Button-1>', lambda e: self.open_news_page(news_urls[0]))
        news0.bind('<Enter>', lambda e: self.news_summary(news_urls[0]))

        news1 = ttk.Label(self, text=headlines[1], image=tk_images[1], compound='right')
        news1.image = tk_images[1]
        news1.grid(row=2, column=0)
        news1.bind('<Button-1>', lambda e: self.open_news_page(news_urls[1]))

        news2 = ttk.Label(self, text=headlines[2], image=tk_images[2], compound='right')
        news2.image = tk_images[2]
        news2.grid(row=3, column=0)
        news2.bind('<Button-1>', lambda e: self.open_news_page(news_urls[2]))

        news3 = ttk.Label(self, text=headlines[3], image=tk_images[3], compound='right')
        news3.image = tk_images[3]
        news3.grid(row=4, column=0)
        news3.bind('<Button-1>', lambda e: self.open_news_page(news_urls[3]))

        news4 = ttk.Label(self, text=headlines[4], image=tk_images[4], compound='right')
        news4.image = tk_images[4]
        news4.grid(row=5, column=0)
        news4.bind('<Button-1>', lambda e: self.open_news_page(news_urls[4]))

        news5 = ttk.Label(self, text=headlines[5], image=tk_images[5], compound='right')
        news5.image = tk_images[5]
        news5.grid(row=1, column=1)
        news5.bind('<Button-1>', lambda e: self.open_news_page(news_urls[5]))

        news6 = ttk.Label(self, text=headlines[6], image=tk_images[6], compound='right')
        news6.image = tk_images[6]
        news6.grid(row=2, column=1)
        news6.bind('<Button-1>', lambda e: self.open_news_page(news_urls[6]))

        news7 = ttk.Label(self, text=headlines[7], image=tk_images[7], compound='right')
        news7.image = tk_images[7]
        news7.grid(row=3, column=1)
        news7.bind('<Button-1>', lambda e: self.open_news_page(news_urls[7]))

        news8 = ttk.Label(self, text=headlines[8], image=tk_images[8], compound='right')
        news8.image = tk_images[8]
        news8.grid(row=4, column=1)
        news8.bind('<Button-1>', lambda e: self.open_news_page(news_urls[8]))

        news9 = ttk.Label(self, text=headlines[9], image=tk_images[9], compound='right')
        news9.image = tk_images[9]
        news9.grid(row=5, column=1)
        news9.bind('<Button-1>', lambda e: self.open_news_page(news_urls[9]))

    def open_news_page(self, news_url):
        webbrowser.open(news_url, new=2, autoraise=True)
                
    def news_summary(self, news_url):

        session = req.HTMLSession()
        r = session.get(news_url)
        summary_xpath = r.html.xpath('//*[@id="leftColumn"]/div[4]', first=True)

        summary_paragraphs = summary_xpath.find('p')
        summary = ''
        for p in summary_paragraphs:
            summary += f'\n{p.text}'

        

class MarketTrends(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.trending_stocks()

    def trending_stocks(self):

        session = req.HTMLSession()
        res = session.get(us.trend_stocks)

        trend_stock1 = res.html.xpath(us.trending_stock1, first=True)
        trend_stock1_name = res.html.xpath(us.trending_stock1_name, first=True)
        trend_stock1_label = ttk.Label(self, text=trend_stock1.text)
        trend_stock1_name_label = ttk.Label(self, text=trend_stock1_name.text)
        
        trend_stock2 = res.html.xpath(us.trending_stock2, first=True)
        trend_stock2_name = res.html.xpath(us.trending_stock2_name, first=True) 
        trend_stock2_label = ttk.Label(self, text=trend_stock2.text)
        trend_stock2_name_label = ttk.Label(self, text=trend_stock2_name.text)

        trend_stock3 = res.html.xpath(us.trending_stock3, first=True)
        trend_stock3_name = res.html.xpath(us.trending_stock3_name, first=True) 
        trend_stock3_label = ttk.Label(self, text=trend_stock3.text)
        trend_stock3_name_label = ttk.Label(self, text=trend_stock3_name.text)

        trend_stock4 = res.html.xpath(us.trending_stock4, first=True)
        trend_stock4_name = res.html.xpath(us.trending_stock4_name, first=True) 
        trend_stock4_label = ttk.Label(self, text=trend_stock4.text)
        trend_stock4_name_label = ttk.Label(self, text=trend_stock4_name.text)

        trend_stock5 = res.html.xpath(us.trending_stock5, first=True)
        trend_stock5_name = res.html.xpath(us.trending_stock5_name, first=True)    
        trend_stock5_label = ttk.Label(self, text=trend_stock5.text)
        trend_stock5_name_label = ttk.Label(self, text=trend_stock5_name.text)
        
        # Grid Management
        trend_stock1_label.grid(row=0, column=0)
        trend_stock1_name_label.grid(row=0, column=1)

        trend_stock2_label.grid(row=1, column=0)
        trend_stock2_name_label.grid(row=1, column=1)

        trend_stock3_label.grid(row=2, column=0)
        trend_stock3_name_label.grid(row=2, column=1)

        trend_stock4_label.grid(row=3, column=0)
        trend_stock4_name_label.grid(row=3, column=1)

        trend_stock5_label.grid(row=4, column=0)
        trend_stock5_name_label.grid(row=4, column=1)

def main():
    root = tk.Tk()
    root.state('zoomed')

    # Configuring styles
    style = ttk.Style()

    main_window = MainWindow(root)
    market_trends = MarketTrends(root)

    main_window.grid(row=0, column=1, sticky='nsew')
    market_trends.grid(row=0, column=0, sticky='nsew')

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=3)

    root.mainloop()

if __name__ == "__main__":
    main()