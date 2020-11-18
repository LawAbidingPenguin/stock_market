import io
import json
import webbrowser
import datetime as dt
import requests_html as req
from string import Template
from PIL import Image, ImageTk

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)

import tkinter as tk
from tkinter import ttk,font

import urls_and_selectors as us

#TODO Learn about ttk Styles
#TODO Display news summary as TopLevel window
#TODO Update MarketTrends with additional info
#TODO Create frames for starting page and ticker window

class MainWindow(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.style = ttk.Style()
        
        # Frames for each page in the MainWindow
        self.ticker_frame = ttk.Frame(self)
        self.start_frame = ttk.Frame(self)

        # Search_company shortcut
        self.search_comp = ttk.Entry(self)
        self.search_comp.grid(row=0, column=0)
        self.search_comp.bind('<KeyRelease>', lambda e: self.search_suggestions(
                                                        self.search_comp.get()))

        self.search_button = ttk.Button(self, text='Search', command=lambda : 
                                       [self.ticker_window(),
                                       self.search_comp.delete(0,tk.END)])
        self.search_button.grid(row=0, column=1, sticky='w')

        # Creating a new window to show search_suggestions
        self.suggs_window = tk.Toplevel(self)
        self.suggs_window.withdraw()

        self.start_window()

    def search_suggestions(self, symbol):
        
        # Destroy all widgets inside TopLevel window
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

    # Displaying ticker info
    def ticker_window(self):
        
        self.start_frame.destroy()

        self.ticker_frame.destroy()
        self.ticker_frame = ttk.Frame(self)
        self.ticker_frame.grid(row=1,column=0)

        ticker = self.search_comp.get()
        name, value, value_change, summary = self.stock_data(ticker) 

        # Creating start date and end date comboxes
        filter_frame = ttk.LabelFrame(self.ticker_frame, text='Filter Graph')
        filter_frame.grid(row=2, column=0, columnspan=4)

        start_label = ttk.Label(filter_frame, text='Start date:')
        end_label = ttk.Label(filter_frame, text='End Date:')      

        days = []
        years = []
        months = []
        for d in range(1,32):
            days.append(d)
        for y in range(2021, 1899, -1):
            years.append(y)
        for m in range(1,13):
            months.append(m)

        start_day = ttk.Combobox(filter_frame, values=days, width=2)
        start_month = ttk.Combobox(filter_frame, values=months, width=2)
        start_year = ttk.Combobox(filter_frame, values=years, width=5)

        end_day = ttk.Combobox(filter_frame, values=days, width=2)
        end_month = ttk.Combobox(filter_frame, values=months, width=2)
        end_year = ttk.Combobox(filter_frame, values=years, width=5)
        
        start_label.grid(row=0, column=0, sticky='w')
        start_day.grid(row=1, column=0, sticky='w')
        start_month.grid(row=1, column=1, sticky='w')
        start_year.grid(row=1, column=2, sticky='w')

        end_label.grid(row=0, column=3, sticky='w', padx=(20,0))
        end_day.grid(row=1, column=3, sticky='w', padx=(20,0))
        end_month.grid(row=1, column=4, sticky='w')
        end_year.grid(row=1, column=5, sticky='w')

        today = str(dt.date.today())
        today = today.split('-')
        year = int(today[0])
        month = int(today[1])
        day = int(today[2])

        end_day.set(day)
        end_month.set(month)
        end_year.set(year)

        start_day.set(day)
        if end_month.get() == '1':
            start_month.set('12')
            start_year.set(end_year.get()-1)
        else:
            start_month.set(str(int(end_month.get())-1))
            start_year.set(year)        

        freq_label = ttk.Label(filter_frame, text='Frequency:')
        frequency = ttk.Combobox(filter_frame, width=8, 
                                               values=['Daily',
                                                       'Weekly',
                                                       'Monthly'])
        freq_label.grid(row=0, column=6, sticky='w', padx=(20,0))                                                         
        frequency.grid(row=1, column=6, sticky='w', padx=(20,0))
        frequency.set('Daily')

        def create_chart():

            chart_frame = ttk.Frame(self.ticker_frame)
            chart_frame.grid(row=3, column=0, columnspan=4)

            symbol = ticker

            s_day = start_day.get()
            s_month = start_month.get()
            s_year = start_year.get()[-2:]

            e_day = end_day.get()
            e_month = end_month.get()
            e_year = end_year.get()[-2:]

            # Creating dates to be turned into timestamps
            s_date = dt.datetime.strptime(f'{s_day}/{s_month}/{s_year}',
                                          '%d/%m/%y')
            e_date = dt.datetime.strptime(f'{e_day}/{e_month}/{e_year}',
                                          '%d/%m/%y')

            # Turning dates into timestamps
            s_time = int(dt.datetime.timestamp(s_date))
            e_time = int(dt.datetime.timestamp(e_date))
            
            # Getting first trade time to notify the user
            session = req.HTMLSession()
            r = session.get('https://query1.finance.yahoo.com/v8/finance/'
                            f'chart/{symbol}?region=US&lang=en-US&'
                            'includePrePost=false&interval=2m&range=1d&'
                            'corsDomain=finance.yahoo.com&.tsrc=finance')
            page_text = json.loads(r.html.text)
            first_trade_time = int(page_text['chart']['result']
                              [0]['meta']['firstTradeDate'])
            # first_trade_time in dd/mm/yy date form
            ftd = dt.datetime.fromtimestamp(first_trade_time).strftime('%d/%m/%y')
            
            # Creating frequency argument
            freq = ''
            if frequency.get() == 'Daily':
                freq = '1d'
            elif frequency.get() == 'Weekly':
                freq = '1wk'
            else:
                freq = '1mo'

            if s_time < first_trade_time or e_time < first_trade_time:
                tk.messagebox.showinfo(title='First Trade Date',
                                       message=f'No trades made before {ftd}')
            else:
                chart_frame.destroy()

                chart_frame = ttk.Frame(self.ticker_frame)
                chart_frame.grid(row=3, column=0, columnspan=4)
                self.chart_data(chart_frame, symbol, s_time, e_time, freq)

        # Initial chart
        create_chart()    

        apply_but = ttk.Button(filter_frame, text='Apply', 
                                             command=create_chart)
        apply_but.grid(row=1, column=7)                                           

        name_label = ttk.Label(self.ticker_frame, text=name)
        value_label = ttk.Label(self.ticker_frame, text=value)
        value_change_label = ttk.Label(self.ticker_frame, text=value_change)

        name_label.grid(row=0, column=0, sticky='w')
        value_label.grid(row=1, column=0, sticky='w')
        value_change_label.grid(row=1, column=0, sticky='ne')

        row = 4
        for k,v in summary.items():
            ttk.Label(self.ticker_frame, text=k).grid(row=row, column=0, sticky='w')
            ttk.Label(self.ticker_frame, text=v).grid(row=row, column=1, sticky='w')
            row += 1

    # Function to be used in ticker_window
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

    # from_date and to_date is to be represented as a timestamp
    def chart_data(self, frame, symbol, from_date, to_date, frequency):

        session = req.HTMLSession()
        r = session.get(f'https://finance.yahoo.com/quote/{symbol}/history?'
                        f'period1={from_date}&period2={to_date}&interval={frequency}'
                        f'&filter=history&frequency={frequency}&includeAdjustedClose=true')

        dates = []
        close_values = []
        elements = r.html.xpath(('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                                 '/section/div[2]/table/tbody/tr'))
        
        # Xpath template
        x_temp = Template(
            '//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
            '/section/div[2]/table/tbody/tr[$tr]/td[$td]/span')

        for n in range(1, len(elements)+1):
            try:
                dates.append(r.html.xpath(x_temp.substitute(tr=n, td=1), first=True).text)

                # Handling close values with a ',' separator (ex: 13,264.67)
                try:
                    c_value = float(r.html.xpath(x_temp.substitute(tr=n, td=5), first=True).text)
                except ValueError:
                    c_value = r.html.xpath(x_temp.substitute(tr=n, td=5), first=True).text
                    c_value = c_value.split(",")
                    c_value = ''.join(c_value)
                    c_value = float(c_value)

                close_values.append(c_value)
            except AttributeError:
                # Handling close values with a ',' separator (ex: 13,264.67)
                try:
                    c_value = float(r.html.xpath(x_temp.substitute(tr=n-1, td=5), first=True).text)
                except ValueError:
                    c_value = r.html.xpath(x_temp.substitute(tr=n-1, td=5), first=True).text
                    c_value = c_value.split(",")
                    c_value = ''.join(c_value)
                    c_value = float(c_value)

                close_values.append(c_value)

        dates.reverse()
        close_values.reverse()
        stocks = {
            'Date': dates,
            'Close': close_values}

        df = pd.DataFrame(stocks, columns=['Date', 'Close'])

        sns.set_style('whitegrid')
        f = plt.Figure(figsize=(6, 4), dpi=100)
        ax = f.subplots()
        ax.set_xticks([])
        sns.lineplot(data=df, x='Date', y='Close', ax=ax)
        canvas = FigureCanvasTkAgg(f, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, ipady=25)

        toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas._tkcanvas.pack()      

    # Home page of the program
    def start_window(self):
        
        self.start_frame.destroy()
        self.start_frame = ttk.Frame(self)
        self.start_frame.grid(row=1,column=0)

        self.top_frame = ttk.Frame(self.start_frame)
        self.worst_frame = ttk.Frame(self.start_frame)
        self.follow_frame = ttk.Frame(self.start_frame)
        self.news_frame = ttk.Frame(self.start_frame)

        self.top_frame.grid(row=1, column=0, columnspan=6)
        self.worst_frame.grid(row=2, column=0, columnspan=6)
        self.follow_frame.grid(row=3, column=0, columnspan=6)
        self.news_frame.grid(row=4, column=0, columnspan=6,
                                              rowspan=4)

        self.get_watchlist(self.top_frame, us.yh_top_perf)
        self.get_watchlist(self.worst_frame, us.yh_worst_perf)
        self.get_watchlist(self.follow_frame, us.yh_most_follow)

        self.news()

    def get_watchlist(self, frame, url):
        
        session = req.HTMLSession()
        r = session.get(url)

        names = []
        urls = []
        images_src = []
        for n in range(1,7):
            info = r.html.xpath(
            '//*[@id="Col1-0-CategoryTable-Proxy"]/section'
            f'/div[2]/div/div/table/tbody/tr[{n}]/td', first=True)

            names.append(info.text)
            urls.append('https://finance.yahoo.com' +
                        info.links.pop())
            
            img_src = info.find('img', first=True)
            img_src = img_src.attrs['src']
            images_src.append(img_src)
            
        images = []
        for img_src in images_src:
            # turning a bytes representation of an image
            # into a format usable by ImageTk.PhotoImage 
            images.append(Image.open(io.BytesIO(session.get(img_src).content)))

        # images to be used in tk widgets
        tk_images = []
        for img in images:
            img.thumbnail((200,200))
            tk_images.append(ImageTk.PhotoImage(img))

        label0 = ttk.Label(frame, text=names[0], image=tk_images[0], 
                          compound='center')
        label0.image = tk_images[0]
        label0.grid(row=1, column=0)

        label1 = ttk.Label(frame, text=names[1], image=tk_images[1], 
                          compound='center')
        label1.image = tk_images[1]
        label1.grid(row=1, column=1)

        label2 = ttk.Label(frame, text=names[2], image=tk_images[2], 
                          compound='center')
        label2.image = tk_images[2]
        label2.grid(row=1, column=2)

        label3 = ttk.Label(frame, text=names[3], image=tk_images[3], 
                          compound='center')
        label3.image = tk_images[3]
        label3.grid(row=1, column=3)

        label4 = ttk.Label(frame, text=names[4], image=tk_images[4], 
                          compound='center')
        label4.image = tk_images[4]
        label4.grid(row=1, column=4)

        label5 = ttk.Label(frame, text=names[5], image=tk_images[5], 
                          compound='center')
        label5.image = tk_images[5]
        label5.grid(row=1, column=5)

    def news(self):
         
        url = us.investing_news
        session = req.HTMLSession()
        r = session.get(url)

        headlines = []
        news_urls = []
        images = []

        # News template
        n_temp = Template('//*[@id="leftColumn"]/div[4]/article[$ar]/div[1]/a')
        a_temp = Template('//*[@id="leftColumn"]/div[4]/article[$ar]/a/img')

        for n in range(1, 13):
            try:
                headlines.append(r.html.xpath(n_temp.substitute(ar=n), first=True).text)
                news_urls.append(r.html.xpath(n_temp.substitute(ar=n), first=True).absolute_links.pop())
                images.append(r.html.xpath(a_temp.substitute(ar=n), first=True).attrs['data-src'])
            except AttributeError:
                headlines.append('NoneTypeObject')
                news_urls.append('NoneTypeObject')
                images.append('NoneTypeObject')

        headlines = [item for item in headlines if item != 'NoneTypeObject']
        news_urls = [item for item in news_urls if item != 'NoneTypeObject']
        images_src = [item for item in images if item != 'NoneTypeObject']
               
        images = []
        for img_src in images_src:
            # turning a bytes representation of an image
            # into a format usable by ImageTk.PhotoImage  
            images.append(Image.open(io.BytesIO(session.get(img_src).content)))

        # images to be used in tk widgets
        tk_images = []
        for img in images:
            tk_images.append(ImageTk.PhotoImage(img))
            
        news0 = ttk.Label(self.news_frame, text=headlines[0], image=tk_images[0], compound='right')
        news0.bind('<Button-1>', lambda e: self.open_news_page(news_urls[0]))
        news0.bind('<Enter>', lambda e: self.news_summary(news_urls[0]))
        news0.image = tk_images[0]
        news0.grid(row=1, column=0)

        news1 = ttk.Label(self.news_frame, text=headlines[1], image=tk_images[1], compound='right')
        news1.bind('<Button-1>', lambda e: self.open_news_page(news_urls[1]))
        news1.image = tk_images[1]
        news1.grid(row=2, column=0)

        news2 = ttk.Label(self.news_frame, text=headlines[2], image=tk_images[2], compound='right')
        news2.bind('<Button-1>', lambda e: self.open_news_page(news_urls[2]))
        news2.image = tk_images[2]
        news2.grid(row=3, column=0)

        news3 = ttk.Label(self.news_frame, text=headlines[3], image=tk_images[3], compound='right')
        news3.bind('<Button-1>', lambda e: self.open_news_page(news_urls[3]))
        news3.image = tk_images[3]
        news3.grid(row=4, column=0)

        news4 = ttk.Label(self.news_frame, text=headlines[4], image=tk_images[4], compound='right')
        news4.bind('<Button-1>', lambda e: self.open_news_page(news_urls[4]))
        news4.image = tk_images[4]
        news4.grid(row=5, column=0)

        news5 = ttk.Label(self.news_frame, text=headlines[5], image=tk_images[5], compound='right')
        news5.bind('<Button-1>', lambda e: self.open_news_page(news_urls[5]))
        news5.image = tk_images[5]
        news5.grid(row=1, column=1)

        news6 = ttk.Label(self.news_frame, text=headlines[6], image=tk_images[6], compound='right')
        news6.bind('<Button-1>', lambda e: self.open_news_page(news_urls[6]))
        news6.image = tk_images[6]
        news6.grid(row=2, column=1)

        news7 = ttk.Label(self.news_frame, text=headlines[7], image=tk_images[7], compound='right')
        news7.bind('<Button-1>', lambda e: self.open_news_page(news_urls[7]))
        news7.image = tk_images[7]
        news7.grid(row=3, column=1)

        news8 = ttk.Label(self.news_frame, text=headlines[8], image=tk_images[8], compound='right')
        news8.bind('<Button-1>', lambda e: self.open_news_page(news_urls[8]))
        news8.image = tk_images[8]
        news8.grid(row=4, column=1)

        news9 = ttk.Label(self.news_frame, text=headlines[9], image=tk_images[9], compound='right')
        news9.bind('<Button-1>', lambda e: self.open_news_page(news_urls[9]))
        news9.image = tk_images[9]
        news9.grid(row=5, column=1)

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

        self.s = ttk.Style()

        self.s.configure('Value.TLabel', foreground='black',
                                         width=10, anchor='e')
        self.s.configure('GrayFont.TLabel', foreground='#5b636a',
                                            width=10, anchor='e')
        self.s.configure('Symbol.TLabel', foreground='#5b636a',
                                            width=10, anchor='w')
        self.s.configure('NameFont.TLabel', foreground='#5b636a',
                                            width=40)                                    
        self.s.configure('Ticker.TLabel', foreground='#0f69ff',
                                          font='TkDefaultFont 9 bold',
                                          width=10)
        self.s.configure('UnderlineTicker.TLabel', foreground='#0f69ff', 
                                                   font='TkDefaultFont 9 bold underline', 
                                                   width=10)                              
        self.s.configure('BoldFont.TLabel', font='TkDefaultFont 15',
                                            foreground='#3b3830')
        self.s.configure('PlusChange.TLabel', foreground='#2abf2c',
                                              width=10, anchor='e')
        self.s.configure('MinusChange.TLabel', foreground='#ff0000',
                                               width=10, anchor='e')
                                               
        self.trending_stocks()
        self.gainers()
        self.losers()

    def trending_stocks(self):

        session = req.HTMLSession()
        res = session.get(us.trend_stocks)

        trend_frame = ttk.Frame(self)
        header_frame = ttk.Frame(trend_frame)

        name = ttk.Label(header_frame, text='Trending Tickers >',
                                       style='BoldFont.TLabel')
        symbol = ttk.Label(header_frame, text='Symbol',
                                       style='Symbol.TLabel')
        last_price = ttk.Label(header_frame, text='Last Price',
                                       style='GrayFont.TLabel')
        change = ttk.Label(header_frame, text='Change',
                                       style='GrayFont.TLabel')
        change_perc = ttk.Label(header_frame, text='% Change',
                                       style='GrayFont.TLabel')
        header_sep = ttk.Separator(header_frame, orient=tk.HORIZONTAL)

        trend1_info = ttk.Frame(trend_frame)
        trend2_info = ttk.Frame(trend_frame)
        trend3_info = ttk.Frame(trend_frame)
        trend4_info = ttk.Frame(trend_frame)
        trend5_info = ttk.Frame(trend_frame)

        trend_stock1_sep = ttk.Separator(trend_frame, orient=tk.HORIZONTAL)
        trend_stock1 = res.html.xpath(us.trending_stock1, first=True)
        trend_stock1_name = res.html.xpath(us.trending_stock1_name, first=True)
        trend_stock1_value = res.html.xpath(us.trending_stock1_value, first=True)
        trend_stock1_change = res.html.xpath(us.trending_stock1_change, first=True)
        trend_stock1_percent = res.html.xpath(us.trending_stock1_percent, first=True)
        trend_stock1_label = ttk.Label(trend1_info, text=f'{trend_stock1.text}',
                                                    style='Ticker.TLabel')
        trend_stock1_name_label = ttk.Label(trend_frame, text=f'{trend_stock1_name.text}',
                                                         style='NameFont.TLabel')
        trend_stock1_value_label = ttk.Label(trend1_info, text=f'{trend_stock1_value.text}',
                                                          style='Value.TLabel')
        trend_stock1_change_label = ttk.Label(trend1_info, text=f'{trend_stock1_change.text}')
        trend_stock1_percent_label = ttk.Label(trend1_info, text=f'{trend_stock1_percent.text}')

        trend_stock2_sep = ttk.Separator(trend_frame, orient=tk.HORIZONTAL)
        trend_stock2 = res.html.xpath(us.trending_stock2, first=True)
        trend_stock2_name = res.html.xpath(us.trending_stock2_name, first=True) 
        trend_stock2_value = res.html.xpath(us.trending_stock2_value, first=True)
        trend_stock2_change = res.html.xpath(us.trending_stock2_change, first=True)
        trend_stock2_percent = res.html.xpath(us.trending_stock2_percent, first=True)
        trend_stock2_label = ttk.Label(trend2_info, text=f'{trend_stock2.text}',
                                                    style='Ticker.TLabel')
        trend_stock2_name_label = ttk.Label(trend_frame, text=f'{trend_stock2_name.text}',
                                                         style='NameFont.TLabel')
        trend_stock2_value_label = ttk.Label(trend2_info, text=f'{trend_stock2_value.text}',
                                                          style='Value.TLabel')
        trend_stock2_change_label = ttk.Label(trend2_info, text=f'{trend_stock2_change.text}')
        trend_stock2_percent_label = ttk.Label(trend2_info, text=f'{trend_stock2_percent.text}')

        trend_stock3_sep = ttk.Separator(trend_frame, orient=tk.HORIZONTAL)
        trend_stock3 = res.html.xpath(us.trending_stock3, first=True)
        trend_stock3_name = res.html.xpath(us.trending_stock3_name, first=True)
        trend_stock3_value = res.html.xpath(us.trending_stock3_value, first=True)
        trend_stock3_change = res.html.xpath(us.trending_stock3_change, first=True)
        trend_stock3_percent = res.html.xpath(us.trending_stock3_percent, first=True) 
        trend_stock3_label = ttk.Label(trend3_info, text=f'{trend_stock3.text}',
                                                    style='Ticker.TLabel')
        trend_stock3_name_label = ttk.Label(trend_frame, text=f'{trend_stock3_name.text}',
                                                         style='NameFont.TLabel')
        trend_stock3_value_label = ttk.Label(trend3_info, text=f'{trend_stock3_value.text}',
                                                          style='Value.TLabel')
        trend_stock3_change_label = ttk.Label(trend3_info, text=f'{trend_stock3_change.text}')
        trend_stock3_percent_label = ttk.Label(trend3_info, text=f'{trend_stock3_percent.text}')

        trend_stock4_sep = ttk.Separator(trend_frame, orient=tk.HORIZONTAL)
        trend_stock4 = res.html.xpath(us.trending_stock4, first=True)
        trend_stock4_name = res.html.xpath(us.trending_stock4_name, first=True)
        trend_stock4_value = res.html.xpath(us.trending_stock4_value, first=True)
        trend_stock4_change = res.html.xpath(us.trending_stock4_change, first=True)
        trend_stock4_percent = res.html.xpath(us.trending_stock4_percent, first=True) 
        trend_stock4_label = ttk.Label(trend4_info, text=f'{trend_stock4.text}',
                                                    style='Ticker.TLabel')
        trend_stock4_name_label = ttk.Label(trend_frame, text=f'{trend_stock4_name.text}',
                                                         style='NameFont.TLabel')
        trend_stock4_value_label = ttk.Label(trend4_info, text=f'{trend_stock4_value.text}',
                                                          style='Value.TLabel')
        trend_stock4_change_label = ttk.Label(trend4_info, text=f'{trend_stock4_change.text}')
        trend_stock4_percent_label = ttk.Label(trend4_info, text=f'{trend_stock4_percent.text}')

        trend_stock5_sep = ttk.Separator(trend_frame, orient=tk.HORIZONTAL)
        trend_stock5 = res.html.xpath(us.trending_stock5, first=True)
        trend_stock5_name = res.html.xpath(us.trending_stock5_name, first=True)
        trend_stock5_value = res.html.xpath(us.trending_stock5_value, first=True)
        trend_stock5_change = res.html.xpath(us.trending_stock5_change, first=True)
        trend_stock5_percent = res.html.xpath(us.trending_stock5_percent, first=True)    
        trend_stock5_label = ttk.Label(trend5_info, text=f'{trend_stock5.text}',
                                                    style='Ticker.TLabel')
        trend_stock5_name_label = ttk.Label(trend_frame, text=f'{trend_stock5_name.text}',
                                                         style='NameFont.TLabel')
        trend_stock5_value_label = ttk.Label(trend5_info, text=f'{trend_stock5_value.text}',
                                                          style='Value.TLabel')
        trend_stock5_change_label = ttk.Label(trend5_info, text=f'{trend_stock5_change.text}')
        trend_stock5_percent_label = ttk.Label(trend5_info, text=f'{trend_stock5_percent.text}')
        
        # GRID MANAGEMENT
        trend_frame.grid(row=0, column=0, pady=(40,0),
                        padx=(20,0), sticky='nesw')
        header_frame.grid(row=0, column=0, columnspan=2,
                         sticky='w')

        name.grid(row=0, column=0, columnspan=4, sticky='w')
        symbol.grid(row=1, column=0, sticky='w')
        last_price.grid(row=1, column=1, sticky='e')
        change.grid(row=1, column=2, sticky='e')
        change_perc.grid(row=1, column=3, sticky='e')
        header_sep.grid(row=2, column=0, columnspan=4, sticky='nesw')
        
        # Tickers
        trend_stock1_label.grid(row=0, column=0, sticky='w')
        trend_stock2_label.grid(row=0, column=0, sticky='w')
        trend_stock3_label.grid(row=0, column=0, sticky='w')
        trend_stock4_label.grid(row=0, column=0, sticky='w')
        trend_stock5_label.grid(row=0, column=0, sticky='w')

        # Values and changes
        trend_stock1_value_label.grid(row=0, column=1, sticky='e')
        trend_stock1_change_label.grid(row=0, column=2, sticky='e')
        trend_stock1_percent_label.grid(row=0, column=3, sticky='e')
        
        trend_stock2_value_label.grid(row=0, column=1, sticky='e')
        trend_stock2_change_label.grid(row=0, column=2, sticky='e')
        trend_stock2_percent_label.grid(row=0, column=3, sticky='e')

        trend_stock3_value_label.grid(row=0, column=1, sticky='e')
        trend_stock3_change_label.grid(row=0, column=2, sticky='e')
        trend_stock3_percent_label.grid(row=0, column=3, sticky='e')

        trend_stock4_value_label.grid(row=0, column=1, sticky='e')
        trend_stock4_change_label.grid(row=0, column=2, sticky='e')
        trend_stock4_percent_label.grid(row=0, column=3, sticky='e')

        trend_stock5_value_label.grid(row=0, column=1, sticky='e')
        trend_stock5_change_label.grid(row=0, column=2, sticky='e')
        trend_stock5_percent_label.grid(row=0, column=3, sticky='e')

        # Setting the styles of each value change
        if '+' in trend_stock1_change.text:
            trend_stock1_change_label.configure(style='PlusChange.TLabel')
            trend_stock1_percent_label.configure(style='PlusChange.TLabel') 
        else:
            trend_stock1_change_label.configure(style='MinusChange.TLabel')
            trend_stock1_percent_label.configure(style='MinusChange.TLabel')

        if '+' in trend_stock2_change.text:
            trend_stock2_change_label.configure(style='PlusChange.TLabel')
            trend_stock2_percent_label.configure(style='PlusChange.TLabel') 
        else:
            trend_stock2_change_label.configure(style='MinusChange.TLabel')
            trend_stock2_percent_label.configure(style='MinusChange.TLabel')

        if '+' in trend_stock3_change.text:
            trend_stock3_change_label.configure(style='PlusChange.TLabel')
            trend_stock3_percent_label.configure(style='PlusChange.TLabel') 
        else:
            trend_stock3_change_label.configure(style='MinusChange.TLabel')
            trend_stock3_percent_label.configure(style='MinusChange.TLabel')

        if '+' in trend_stock4_change.text:
            trend_stock4_change_label.configure(style='PlusChange.TLabel')
            trend_stock4_percent_label.configure(style='PlusChange.TLabel') 
        else:
            trend_stock4_change_label.configure(style='MinusChange.TLabel')
            trend_stock4_percent_label.configure(style='MinusChange.TLabel')

        if '+' in trend_stock5_change.text:
            trend_stock5_change_label.configure(style='PlusChange.TLabel')
            trend_stock5_percent_label.configure(style='PlusChange.TLabel') 
        else:
            trend_stock5_change_label.configure(style='MinusChange.TLabel')
            trend_stock5_percent_label.configure(style='MinusChange.TLabel')

        # Frames for each stock
        trend1_info.grid(row=1, column=0, columnspan=4, sticky='w')
        trend2_info.grid(row=4, column=0, columnspan=4, sticky='w')
        trend3_info.grid(row=7, column=0, columnspan=4, sticky='w')
        trend4_info.grid(row=10, column=0, columnspan=4, sticky='w')
        trend5_info.grid(row=13, column=0, columnspan=4, sticky='w')

        # Company names
        trend_stock1_name_label.grid(row=2, column=0, sticky='sw')
        trend_stock2_name_label.grid(row=5, column=0, sticky='sw')
        trend_stock3_name_label.grid(row=8, column=0, sticky='sw')
        trend_stock4_name_label.grid(row=11, column=0, sticky='sw')
        trend_stock5_name_label.grid(row=14, column=0, sticky='sw')

        # Ttk Separators
        trend_stock1_sep.grid(row=3, column=0, columnspan=4, sticky='nesw')
        trend_stock2_sep.grid(row=6, column=0, columnspan=4, sticky='nesw')
        trend_stock3_sep.grid(row=9, column=0, columnspan=4, sticky='nesw')
        trend_stock4_sep.grid(row=12, column=0, columnspan=4, sticky='nesw')
        trend_stock5_sep.grid(row=15, column=0, columnspan=4, sticky='nesw')

        # Bindings
        trend_stock1_label.bind('<Enter>', lambda e:
                               trend_stock1_label.configure(style='UnderlineTicker.TLabel'))
        trend_stock1_label.bind('<Leave>', lambda e:
                               trend_stock1_label.configure(style='Ticker.TLabel'))

        trend_stock2_label.bind('<Enter>', lambda e:
                               trend_stock2_label.configure(style='UnderlineTicker.TLabel'))
        trend_stock2_label.bind('<Leave>', lambda e:
                               trend_stock2_label.configure(style='Ticker.TLabel'))

        trend_stock3_label.bind('<Enter>', lambda e:
                               trend_stock3_label.configure(style='UnderlineTicker.TLabel'))
        trend_stock3_label.bind('<Leave>', lambda e:
                               trend_stock3_label.configure(style='Ticker.TLabel'))

        trend_stock4_label.bind('<Enter>', lambda e:
                               trend_stock4_label.configure(style='UnderlineTicker.TLabel'))
        trend_stock4_label.bind('<Leave>', lambda e:
                               trend_stock4_label.configure(style='Ticker.TLabel'))

        trend_stock5_label.bind('<Enter>', lambda e:
                               trend_stock5_label.configure(style='UnderlineTicker.TLabel'))
        trend_stock5_label.bind('<Leave>', lambda e:
                               trend_stock5_label.configure(style='Ticker.TLabel'))    
  
    def gainers(self):

        session = req.HTMLSession()
        r = session.get('https://finance.yahoo.com/gainers')

        gainers_frame = ttk.Frame(self)
        header_frame = ttk.Frame(gainers_frame)

        name = ttk.Label(header_frame, text='Stocks:Gainers >',
                                       style='BoldFont.TLabel')
        symbol = ttk.Label(header_frame, text="Symbol",
                                         style='Symbol.TLabel')
        last_price = ttk.Label(header_frame, text="Last Price",
                                             style='GrayFont.TLabel')
        change = ttk.Label(header_frame, text="Change",
                                         style='GrayFont.TLabel')
        change_perc = ttk.Label(header_frame, text="% Change",
                                              style='GrayFont.TLabel')
        header_sep = ttk.Separator(header_frame, orient=tk.HORIZONTAL)

        gain1_info = ttk.Frame(gainers_frame)
        gain2_info = ttk.Frame(gainers_frame)
        gain3_info = ttk.Frame(gainers_frame)
        gain4_info = ttk.Frame(gainers_frame)
        gain5_info = ttk.Frame(gainers_frame)

        gain_stock1_sep = ttk.Separator(gainers_frame, orient=tk.HORIZONTAL)        
        gain_stock1 = r.html.xpath(us.gainer_stock1, first=True)
        gain_stock1_name = r.html.xpath(us.gainer_stock1_name, first=True)
        gain_stock1_value = r.html.xpath(us.gainer_stock1_value, first=True)
        gain_stock1_change = r.html.xpath(us.gainer_stock1_change, first=True)
        gain_stock1_percent = r.html.xpath(us.gainer_stock1_percent, first=True)
        gain_stock1_label = ttk.Label(gain1_info, text=f'{gain_stock1.text}',
                                                  style='Ticker.TLabel')
        gain_stock1_name_label = ttk.Label(gainers_frame, text=f'{gain_stock1_name.text}',
                                                          style='NameFont.TLabel')
        gain_stock1_value_label = ttk.Label(gain1_info, text=f'{gain_stock1_value.text}',
                                                        style='Value.TLabel')
        gain_stock1_change_label = ttk.Label(gain1_info, text=f'{gain_stock1_change.text}')
        gain_stock1_percent_label = ttk.Label(gain1_info, text=f'{gain_stock1_percent.text}')

        gain_stock2_sep = ttk.Separator(gainers_frame, orient=tk.HORIZONTAL)
        gain_stock2 = r.html.xpath(us.gainer_stock2, first=True)
        gain_stock2_name = r.html.xpath(us.gainer_stock2_name, first=True) 
        gain_stock2_value = r.html.xpath(us.gainer_stock2_value, first=True)
        gain_stock2_change = r.html.xpath(us.gainer_stock2_change, first=True)
        gain_stock2_percent = r.html.xpath(us.gainer_stock2_percent, first=True)
        gain_stock2_label = ttk.Label(gain2_info, text=f'{gain_stock2.text}',
                                                  style='Ticker.TLabel')
        gain_stock2_name_label = ttk.Label(gainers_frame, text=f'{gain_stock2_name.text}',
                                                          style='NameFont.TLabel')
        gain_stock2_value_label = ttk.Label(gain2_info, text=f'{gain_stock2_value.text}',
                                                        style='Value.TLabel')
        gain_stock2_change_label = ttk.Label(gain2_info, text=f'{gain_stock2_change.text}')
        gain_stock2_percent_label = ttk.Label(gain2_info, text=f'{gain_stock2_percent.text}')

        gain_stock3_sep = ttk.Separator(gainers_frame, orient=tk.HORIZONTAL)
        gain_stock3 = r.html.xpath(us.gainer_stock3, first=True)
        gain_stock3_name = r.html.xpath(us.gainer_stock3_name, first=True)
        gain_stock3_value = r.html.xpath(us.gainer_stock3_value, first=True)
        gain_stock3_change = r.html.xpath(us.gainer_stock3_change, first=True)
        gain_stock3_percent = r.html.xpath(us.gainer_stock3_percent, first=True) 
        gain_stock3_label = ttk.Label(gain3_info, text=f'{gain_stock3.text}',
                                                  style='Ticker.TLabel')
        gain_stock3_name_label = ttk.Label(gainers_frame, text=f'{gain_stock3_name.text}',
                                                          style='NameFont.TLabel')
        gain_stock3_value_label = ttk.Label(gain3_info, text=f'{gain_stock3_value.text}',
                                                        style='Value.TLabel')
        gain_stock3_change_label = ttk.Label(gain3_info, text=f'{gain_stock3_change.text}')
        gain_stock3_percent_label = ttk.Label(gain3_info, text=f'{gain_stock3_percent.text}')

        gain_stock4_sep = ttk.Separator(gainers_frame, orient=tk.HORIZONTAL)
        gain_stock4 = r.html.xpath(us.gainer_stock4, first=True)
        gain_stock4_name = r.html.xpath(us.gainer_stock4_name, first=True)
        gain_stock4_value = r.html.xpath(us.gainer_stock4_value, first=True)
        gain_stock4_change = r.html.xpath(us.gainer_stock4_change, first=True)
        gain_stock4_percent = r.html.xpath(us.gainer_stock4_percent, first=True) 
        gain_stock4_label = ttk.Label(gain4_info, text=f'{gain_stock4.text}',
                                                  style='Ticker.TLabel')
        gain_stock4_name_label = ttk.Label(gainers_frame, text=f'{gain_stock4_name.text}',
                                                          style='NameFont.TLabel')
        gain_stock4_value_label = ttk.Label(gain4_info, text=f'{gain_stock4_value.text}',
                                                        style='Value.TLabel')
        gain_stock4_change_label = ttk.Label(gain4_info, text=f'{gain_stock4_change.text}')
        gain_stock4_percent_label = ttk.Label(gain4_info, text=f'{gain_stock4_percent.text}')

        gain_stock5_sep = ttk.Separator(gainers_frame, orient=tk.HORIZONTAL)
        gain_stock5 = r.html.xpath(us.gainer_stock5, first=True)
        gain_stock5_name = r.html.xpath(us.gainer_stock5_name, first=True)
        gain_stock5_value = r.html.xpath(us.gainer_stock5_value, first=True)
        gain_stock5_change = r.html.xpath(us.gainer_stock5_change, first=True)
        gain_stock5_percent = r.html.xpath(us.gainer_stock5_percent, first=True)    
        gain_stock5_label = ttk.Label(gain5_info, text=f'{gain_stock5.text}',
                                                  style='Ticker.TLabel')
        gain_stock5_name_label = ttk.Label(gainers_frame, text=f'{gain_stock5_name.text}',
                                                          style='NameFont.TLabel')
        gain_stock5_value_label = ttk.Label(gain5_info, text=f'{gain_stock5_value.text}',
                                                        style='Value.TLabel')
        gain_stock5_change_label = ttk.Label(gain5_info, text=f'{gain_stock5_change.text}')
        gain_stock5_percent_label = ttk.Label(gain5_info, text=f'{gain_stock5_percent.text}')
        
        # GRID MANAGEMENT
        gainers_frame.grid(row=1, column=0, pady=(40,0),
                          padx=(20,0), sticky='nesw')
        header_frame.grid(row=0, column=0, columnspan=2,
                         sticky='w')

        name.grid(row=0, column=0, columnspan=4, sticky='w')
        symbol.grid(row=1, column=0, sticky='w')
        last_price.grid(row=1, column=1, sticky='e')
        change.grid(row=1, column=2, sticky='e')
        change_perc.grid(row=1, column=3, sticky='e')
        header_sep.grid(row=2, column=0, columnspan=4, sticky='nesw')

        # Tickers
        gain_stock1_label.grid(row=0, column=0, sticky='w')
        gain_stock2_label.grid(row=0, column=0, sticky='w')
        gain_stock3_label.grid(row=0, column=0, sticky='w')
        gain_stock4_label.grid(row=0, column=0, sticky='w')
        gain_stock5_label.grid(row=0, column=0, sticky='w')
        
        # Values and changes
        gain_stock1_value_label.grid(row=0, column=1, sticky='e')
        gain_stock1_change_label.grid(row=0, column=2, sticky='e')
        gain_stock1_percent_label.grid(row=0, column=3, sticky='e')
        
        gain_stock2_value_label.grid(row=0, column=1, sticky='e')
        gain_stock2_change_label.grid(row=0, column=2, sticky='e')
        gain_stock2_percent_label.grid(row=0, column=3, sticky='e')

        gain_stock3_value_label.grid(row=0, column=1, sticky='e')
        gain_stock3_change_label.grid(row=0, column=2, sticky='e')
        gain_stock3_percent_label.grid(row=0, column=3, sticky='e')

        gain_stock4_value_label.grid(row=0, column=1, sticky='e')
        gain_stock4_change_label.grid(row=0, column=2, sticky='e')
        gain_stock4_percent_label.grid(row=0, column=3, sticky='e')

        gain_stock5_value_label.grid(row=0, column=1, sticky='e')
        gain_stock5_change_label.grid(row=0, column=2, sticky='e')
        gain_stock5_percent_label.grid(row=0, column=3, sticky='e')

        # Setting the styles of each value change
        if '+' in gain_stock1_change.text:
            gain_stock1_change_label.configure(style='PlusChange.TLabel')
            gain_stock1_percent_label.configure(style='PlusChange.TLabel') 
        else:
            gain_stock1_change_label.configure(style='MinusChange.TLabel')
            gain_stock1_percent_label.configure(style='MinusChange.TLabel')

        if '+' in gain_stock2_change.text:
            gain_stock2_change_label.configure(style='PlusChange.TLabel')
            gain_stock2_percent_label.configure(style='PlusChange.TLabel') 
        else:
            gain_stock2_change_label.configure(style='MinusChange.TLabel')
            gain_stock2_percent_label.configure(style='MinusChange.TLabel')

        if '+' in gain_stock3_change.text:
            gain_stock3_change_label.configure(style='PlusChange.TLabel')
            gain_stock3_percent_label.configure(style='PlusChange.TLabel') 
        else:
            gain_stock3_change_label.configure(style='MinusChange.TLabel')
            gain_stock3_percent_label.configure(style='MinusChange.TLabel')

        if '+' in gain_stock4_change.text:
            gain_stock4_change_label.configure(style='PlusChange.TLabel')
            gain_stock4_percent_label.configure(style='PlusChange.TLabel') 
        else:
            gain_stock4_change_label.configure(style='MinusChange.TLabel')
            gain_stock4_percent_label.configure(style='MinusChange.TLabel')

        if '+' in gain_stock5_change.text:
            gain_stock5_change_label.configure(style='PlusChange.TLabel')
            gain_stock5_percent_label.configure(style='PlusChange.TLabel') 
        else:
            gain_stock5_change_label.configure(style='MinusChange.TLabel')
            gain_stock5_percent_label.configure(style='MinusChange.TLabel')

        # Frames for each stock
        gain1_info.grid(row=1, column=0, columnspan=4, sticky='w')
        gain2_info.grid(row=4, column=0, columnspan=4, sticky='w')
        gain3_info.grid(row=7, column=0, columnspan=4, sticky='w')
        gain4_info.grid(row=10, column=0, columnspan=4, sticky='w')
        gain5_info.grid(row=13, column=0, columnspan=4, sticky='w')

        # Company names
        gain_stock1_name_label.grid(row=2, column=0, sticky='sw')
        gain_stock2_name_label.grid(row=5, column=0, sticky='sw')
        gain_stock3_name_label.grid(row=8, column=0, sticky='sw')
        gain_stock4_name_label.grid(row=11, column=0, sticky='sw')
        gain_stock5_name_label.grid(row=14, column=0, sticky='sw')

        # Ttk Separators
        gain_stock1_sep.grid(row=3, column=0, columnspan=4, sticky='nesw')
        gain_stock2_sep.grid(row=6, column=0, columnspan=4, sticky='nesw')
        gain_stock3_sep.grid(row=9, column=0, columnspan=4, sticky='nesw')
        gain_stock4_sep.grid(row=12, column=0, columnspan=4, sticky='nesw')
        gain_stock5_sep.grid(row=15, column=0, columnspan=4, sticky='nesw')

        # Bindings
        gain_stock1_label.bind('<Enter>', lambda e:
                               gain_stock1_label.configure(style='UnderlineTicker.TLabel'))
        gain_stock1_label.bind('<Leave>', lambda e:
                               gain_stock1_label.configure(style='Ticker.TLabel'))

        gain_stock2_label.bind('<Enter>', lambda e:
                               gain_stock2_label.configure(style='UnderlineTicker.TLabel'))
        gain_stock2_label.bind('<Leave>', lambda e:
                               gain_stock2_label.configure(style='Ticker.TLabel'))

        gain_stock3_label.bind('<Enter>', lambda e:
                               gain_stock3_label.configure(style='UnderlineTicker.TLabel'))
        gain_stock3_label.bind('<Leave>', lambda e:
                               gain_stock3_label.configure(style='Ticker.TLabel'))

        gain_stock4_label.bind('<Enter>', lambda e:
                               gain_stock4_label.configure(style='UnderlineTicker.TLabel'))
        gain_stock4_label.bind('<Leave>', lambda e:
                               gain_stock4_label.configure(style='Ticker.TLabel'))

        gain_stock5_label.bind('<Enter>', lambda e:
                               gain_stock5_label.configure(style='UnderlineTicker.TLabel'))
        gain_stock5_label.bind('<Leave>', lambda e:
                               gain_stock5_label.configure(style='Ticker.TLabel'))

    def losers(self):

        session = req.HTMLSession()
        r = session.get('https://finance.yahoo.com/losers')

        losers_frame = ttk.Frame(self)
        header_frame = ttk.Frame(losers_frame)

        name = ttk.Label(header_frame, text='Stocks:Losers >',
                                       style='BoldFont.TLabel')
        symbol = ttk.Label(header_frame, text="Symbol",
                                         style='Symbol.TLabel')
        last_price = ttk.Label(header_frame, text="Last Price",
                                             style='GrayFont.TLabel')
        change = ttk.Label(header_frame, text="Change",
                                         style='GrayFont.TLabel')
        change_perc = ttk.Label(header_frame, text="% Change",
                                              style='GrayFont.TLabel')
        header_sep = ttk.Separator(header_frame, orient=tk.HORIZONTAL)

        lose1_info = ttk.Frame(losers_frame)
        lose2_info = ttk.Frame(losers_frame)
        lose3_info = ttk.Frame(losers_frame)
        lose4_info = ttk.Frame(losers_frame)
        lose5_info = ttk.Frame(losers_frame)

        lose_stock1_sep = ttk.Separator(losers_frame, orient=tk.HORIZONTAL)        
        lose_stock1 = r.html.xpath(us.loser_stock1, first=True)
        lose_stock1_name = r.html.xpath(us.loser_stock1_name, first=True)
        lose_stock1_value = r.html.xpath(us.loser_stock1_value, first=True)
        lose_stock1_change = r.html.xpath(us.loser_stock1_change, first=True)
        lose_stock1_percent = r.html.xpath(us.loser_stock1_percent, first=True)
        lose_stock1_label = ttk.Label(lose1_info, text=f'{lose_stock1.text}',
                                                  style='Ticker.TLabel')
        lose_stock1_name_label = ttk.Label(losers_frame, text=f'{lose_stock1_name.text}',
                                                         style='NameFont.TLabel')
        lose_stock1_value_label = ttk.Label(lose1_info, text=f'{lose_stock1_value.text}',
                                                        style='Value.TLabel')
        lose_stock1_change_label = ttk.Label(lose1_info, text=f'{lose_stock1_change.text}')
        lose_stock1_percent_label = ttk.Label(lose1_info, text=f'{lose_stock1_percent.text}')

        lose_stock2_sep = ttk.Separator(losers_frame, orient=tk.HORIZONTAL)
        lose_stock2 = r.html.xpath(us.loser_stock2, first=True)
        lose_stock2_name = r.html.xpath(us.loser_stock2_name, first=True) 
        lose_stock2_value = r.html.xpath(us.loser_stock2_value, first=True)
        lose_stock2_change = r.html.xpath(us.loser_stock2_change, first=True)
        lose_stock2_percent = r.html.xpath(us.loser_stock2_percent, first=True)
        lose_stock2_label = ttk.Label(lose2_info, text=f'{lose_stock2.text}',
                                                  style='Ticker.TLabel')
        lose_stock2_name_label = ttk.Label(losers_frame, text=f'{lose_stock2_name.text}',
                                                         style='NameFont.TLabel')
        lose_stock2_value_label = ttk.Label(lose2_info, text=f'{lose_stock2_value.text}',
                                                        style='Value.TLabel')
        lose_stock2_change_label = ttk.Label(lose2_info, text=f'{lose_stock2_change.text}')
        lose_stock2_percent_label = ttk.Label(lose2_info, text=f'{lose_stock2_percent.text}')

        lose_stock3_sep = ttk.Separator(losers_frame, orient=tk.HORIZONTAL)
        lose_stock3 = r.html.xpath(us.loser_stock3, first=True)
        lose_stock3_name = r.html.xpath(us.loser_stock3_name, first=True)
        lose_stock3_value = r.html.xpath(us.loser_stock3_value, first=True)
        lose_stock3_change = r.html.xpath(us.loser_stock3_change, first=True)
        lose_stock3_percent = r.html.xpath(us.loser_stock3_percent, first=True) 
        lose_stock3_label = ttk.Label(lose3_info, text=f'{lose_stock3.text}',
                                                  style='Ticker.TLabel')
        lose_stock3_name_label = ttk.Label(losers_frame, text=f'{lose_stock3_name.text}',
                                                         style='NameFont.TLabel')
        lose_stock3_value_label = ttk.Label(lose3_info, text=f'{lose_stock3_value.text}',
                                                        style='Value.TLabel')
        lose_stock3_change_label = ttk.Label(lose3_info, text=f'{lose_stock3_change.text}')
        lose_stock3_percent_label = ttk.Label(lose3_info, text=f'{lose_stock3_percent.text}')

        lose_stock4_sep = ttk.Separator(losers_frame, orient=tk.HORIZONTAL)
        lose_stock4 = r.html.xpath(us.loser_stock4, first=True)
        lose_stock4_name = r.html.xpath(us.loser_stock4_name, first=True)
        lose_stock4_value = r.html.xpath(us.loser_stock4_value, first=True)
        lose_stock4_change = r.html.xpath(us.loser_stock4_change, first=True)
        lose_stock4_percent = r.html.xpath(us.loser_stock4_percent, first=True) 
        lose_stock4_label = ttk.Label(lose4_info, text=f'{lose_stock4.text}',
                                                  style='Ticker.TLabel')
        lose_stock4_name_label = ttk.Label(losers_frame, text=f'{lose_stock4_name.text}',
                                                         style='NameFont.TLabel')
        lose_stock4_value_label = ttk.Label(lose4_info, text=f'{lose_stock4_value.text}',
                                                        style='Value.TLabel')
        lose_stock4_change_label = ttk.Label(lose4_info, text=f'{lose_stock4_change.text}')
        lose_stock4_percent_label = ttk.Label(lose4_info, text=f'{lose_stock4_percent.text}')

        lose_stock5_sep = ttk.Separator(losers_frame, orient=tk.HORIZONTAL)
        lose_stock5 = r.html.xpath(us.loser_stock5, first=True)
        lose_stock5_name = r.html.xpath(us.loser_stock5_name, first=True)
        lose_stock5_value = r.html.xpath(us.loser_stock5_value, first=True)
        lose_stock5_change = r.html.xpath(us.loser_stock5_change, first=True)
        lose_stock5_percent = r.html.xpath(us.loser_stock5_percent, first=True)    
        lose_stock5_label = ttk.Label(lose5_info, text=f'{lose_stock5.text}',
                                                  style='Ticker.TLabel')
        lose_stock5_name_label = ttk.Label(losers_frame, text=f'{lose_stock5_name.text}',
                                                         style='NameFont.TLabel')
        lose_stock5_value_label = ttk.Label(lose5_info, text=f'{lose_stock5_value.text}',
                                                        style='Value.TLabel')
        lose_stock5_change_label = ttk.Label(lose5_info, text=f'{lose_stock5_change.text}')
        lose_stock5_percent_label = ttk.Label(lose5_info, text=f'{lose_stock5_percent.text}')
        
        # GRID MANAGEMENT
        losers_frame.grid(row=2, column=0, pady=(40,0),
                         padx=(20,0), sticky='nesw')
        header_frame.grid(row=0, column=0, columnspan=4,
                         sticky='w')

        name.grid(row=0, column=0, columnspan=4, sticky='w')
        symbol.grid(row=1, column=0, sticky='w')
        last_price.grid(row=1, column=1, sticky='e')
        change.grid(row=1, column=2, sticky='e')
        change_perc.grid(row=1, column=3, sticky='e')
        header_sep.grid(row=2, column=0, columnspan=4, sticky='nesw')

        # Tickers
        lose_stock1_label.grid(row=0, column=0, sticky='w')
        lose_stock2_label.grid(row=0, column=0, sticky='w')
        lose_stock3_label.grid(row=0, column=0, sticky='w')
        lose_stock4_label.grid(row=0, column=0, sticky='w')
        lose_stock5_label.grid(row=0, column=0, sticky='w')
        
        # Values and changes
        lose_stock1_value_label.grid(row=0, column=1, sticky='e')
        lose_stock1_change_label.grid(row=0, column=2, sticky='e')
        lose_stock1_percent_label.grid(row=0, column=3, sticky='e')
        
        lose_stock2_value_label.grid(row=0, column=1, sticky='e')
        lose_stock2_change_label.grid(row=0, column=2, sticky='e')
        lose_stock2_percent_label.grid(row=0, column=3, sticky='e')

        lose_stock3_value_label.grid(row=0, column=1, sticky='e')
        lose_stock3_change_label.grid(row=0, column=2, sticky='e')
        lose_stock3_percent_label.grid(row=0, column=3, sticky='e')

        lose_stock4_value_label.grid(row=0, column=1, sticky='e')
        lose_stock4_change_label.grid(row=0, column=2, sticky='e')
        lose_stock4_percent_label.grid(row=0, column=3, sticky='e')

        lose_stock5_value_label.grid(row=0, column=1, sticky='e')
        lose_stock5_change_label.grid(row=0, column=2, sticky='e')
        lose_stock5_percent_label.grid(row=0, column=3, sticky='e')

        # Setting the styles of each value change
        if '+' in lose_stock1_change.text:
            lose_stock1_change_label.configure(style='PlusChange.TLabel')
            lose_stock1_percent_label.configure(style='PlusChange.TLabel') 
        else:
            lose_stock1_change_label.configure(style='MinusChange.TLabel')
            lose_stock1_percent_label.configure(style='MinusChange.TLabel')

        if '+' in lose_stock2_change.text:
            lose_stock2_change_label.configure(style='PlusChange.TLabel')
            lose_stock2_percent_label.configure(style='PlusChange.TLabel') 
        else:
            lose_stock2_change_label.configure(style='MinusChange.TLabel')
            lose_stock2_percent_label.configure(style='MinusChange.TLabel')

        if '+' in lose_stock3_change.text:
            lose_stock3_change_label.configure(style='PlusChange.TLabel')
            lose_stock3_percent_label.configure(style='PlusChange.TLabel') 
        else:
            lose_stock3_change_label.configure(style='MinusChange.TLabel')
            lose_stock3_percent_label.configure(style='MinusChange.TLabel')

        if '+' in lose_stock4_change.text:
            lose_stock4_change_label.configure(style='PlusChange.TLabel')
            lose_stock4_percent_label.configure(style='PlusChange.TLabel') 
        else:
            lose_stock4_change_label.configure(style='MinusChange.TLabel')
            lose_stock4_percent_label.configure(style='MinusChange.TLabel')

        if '+' in lose_stock5_change.text:
            lose_stock5_change_label.configure(style='PlusChange.TLabel')
            lose_stock5_percent_label.configure(style='PlusChange.TLabel') 
        else:
            lose_stock5_change_label.configure(style='MinusChange.TLabel')
            lose_stock5_percent_label.configure(style='MinusChange.TLabel')

        # Frames for eack stock
        lose1_info.grid(row=1, column=0, columnspan=4, sticky='w')
        lose2_info.grid(row=4, column=0, columnspan=4, sticky='w')
        lose3_info.grid(row=7, column=0, columnspan=4, sticky='w')
        lose4_info.grid(row=10, column=0, columnspan=4, sticky='w')
        lose5_info.grid(row=13, column=0, columnspan=4, sticky='w')        

        # Company names
        lose_stock1_name_label.grid(row=2, column=0, sticky='sw')
        lose_stock2_name_label.grid(row=5, column=0, sticky='sw')
        lose_stock3_name_label.grid(row=8, column=0, sticky='sw')
        lose_stock4_name_label.grid(row=11, column=0, sticky='sw')
        lose_stock5_name_label.grid(row=14, column=0, sticky='sw')

        # Ttk separators
        lose_stock1_sep.grid(row=3, column=0, columnspan=4, sticky='nesw')        
        lose_stock2_sep.grid(row=6, column=0, columnspan=4, sticky='nesw')        
        lose_stock3_sep.grid(row=9, column=0, columnspan=4, sticky='nesw')        
        lose_stock4_sep.grid(row=12, column=0, columnspan=4, sticky='nesw')        
        lose_stock5_sep.grid(row=15, column=0, columnspan=4, sticky='nesw')

        # Bindings
        lose_stock1_label.bind('<Enter>', lambda e:
                               lose_stock1_label.configure(style='UnderlineTicker.TLabel'))
        lose_stock1_label.bind('<Leave>', lambda e:
                               lose_stock1_label.configure(style='Ticker.TLabel'))

        lose_stock2_label.bind('<Enter>', lambda e:
                               lose_stock2_label.configure(style='UnderlineTicker.TLabel'))
        lose_stock2_label.bind('<Leave>', lambda e:
                               lose_stock2_label.configure(style='Ticker.TLabel'))

        lose_stock3_label.bind('<Enter>', lambda e:
                               lose_stock3_label.configure(style='UnderlineTicker.TLabel'))
        lose_stock3_label.bind('<Leave>', lambda e:
                               lose_stock3_label.configure(style='Ticker.TLabel'))

        lose_stock4_label.bind('<Enter>', lambda e:
                               lose_stock4_label.configure(style='UnderlineTicker.TLabel'))
        lose_stock4_label.bind('<Leave>', lambda e:
                               lose_stock4_label.configure(style='Ticker.TLabel'))

        lose_stock5_label.bind('<Enter>', lambda e:
                               lose_stock5_label.configure(style='UnderlineTicker.TLabel'))
        lose_stock5_label.bind('<Leave>', lambda e:
                               lose_stock5_label.configure(style='Ticker.TLabel'))
        
def main():
    root = tk.Tk()
    root.state('zoomed')

    s = ttk.Style()

    main_window = MainWindow(root)
    market_trends = MarketTrends(root)

    main_window.grid(row=0, column=1, sticky='nsew')
    market_trends.grid(row=0, column=0, sticky='nsew')

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=3)

    root.mainloop()

if __name__ == "__main__":
    main()