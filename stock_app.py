import json
import requests_html as req
import tkinter as tk
from tkinter import ttk
import urls_and_selectors as us

#TODO create all the frames needed and color them to show the layout of the program

class MainWindow(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent

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

        name_label.grid(row=1, column=0 ,columnspan=4, sticky='W')
        value_label.grid(row=2, column=0, columnspan=2, sticky='E')
        value_change_label.grid(row=2, column=2, columnspan=2, sticky='W')

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
                
class StockFilters(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent

    def trending_stocks(self):

        session = req.HTMLSession()
        res = session.get('https://finance.yahoo.com/trending-tickers/')

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

    MainWindow(root, bg='red').grid(row=0, column=0, columnspan=2)
    StockFilters(root, bg='blue').grid(row=1, column=0)


    root.mainloop()

if __name__ == "__main__":
    main()