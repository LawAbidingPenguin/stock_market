# URLS
trend_stocks = 'https://finance.yahoo.com/trending-tickers/'
google_news = 'https://www.google.com/search?q=stock+news&source=lmns&tbm=nws&bih=937&biw=1920&hl=en&sa=X&ved=2ahUKEwi545mF063sAhWS0YUKHXlFDfYQ_AUoAXoECAEQAQ'
investing_news = 'https://www.investing.com/news/stock-market-news'
yh_watchlist = 'https://finance.yahoo.com/watchlists'
# Watchlist Top Performers
yh_top_perf = 'https://finance.yahoo.com/watchlists/category/section-gainers'
# Watchlist Worst Performers
yh_worst_perf = 'https://finance.yahoo.com/watchlists/category/section-losers'
# Watchlist Most Followed
yh_most_follow = 'https://finance.yahoo.com/watchlists/category/section-popular'


# XPATH SELECTORS
# News info
news_title = '//*[@id="leftColumn"]/h1'
news_summary = '//*[@id="leftColumn"]/div[3]'

# Watchlist info
wl_title = '//*[@id="Col1-0-CategoryTable-Proxy"]/section/div[1]/h1'
wl_url = '//*[@id="Col1-0-WatchlistDetail-Proxy"]/div/section[3]/div/div/table/tbody'

# Company info
company_name = '//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1'

# Stock info
stock_value = '//*[@id="quote-header-info"]/div[3]/div[1]/div/span[1]'
value_change = '//*[@id="quote-header-info"]/div[3]/div[1]/div/span[2]'
summary = '//*[@id="quote-summary"]'

# Displays current trending stocks
trending_stock1 = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[1]/td[1]/a'
trending_stock1_name = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[1]/td[2]'
trending_stock1_value = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[1]/td[3]'
trending_stock1_change = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[1]/td[5]/span'
trending_stock1_percent = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[1]/td[6]/span'

trending_stock2 = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[2]/td[1]/a'
trending_stock2_name = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[2]/td[2]'
trending_stock2_value = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[2]/td[3]'
trending_stock2_change = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[2]/td[5]/span'
trending_stock2_percent = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[2]/td[6]/span'

trending_stock3 = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[3]/td[1]/a'
trending_stock3_name = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[3]/td[2]'
trending_stock3_value = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[3]/td[3]'
trending_stock3_change = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[3]/td[5]/span'
trending_stock3_percent = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[3]/td[6]/span'

trending_stock4 = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[4]/td[1]/a'
trending_stock4_name = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[4]/td[2]'
trending_stock4_value = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[4]/td[3]'
trending_stock4_change = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[4]/td[5]/span'
trending_stock4_percent = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[4]/td[6]/span'

trending_stock5 = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[5]/td[1]/a'
trending_stock5_name = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[5]/td[2]'
trending_stock5_value = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[5]/td[3]'
trending_stock5_change = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[5]/td[5]/span'
trending_stock5_percent = '//*[@id="yfin-list"]/div[2]/div/div/table/tbody/tr[5]/td[6]/span'

# Displays biggest gainers
gainer_stock1 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[1]/a'
gainer_stock1_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[2]'
gainer_stock1_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[3]/span'
gainer_stock1_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[4]/span'
gainer_stock1_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[5]/span'

gainer_stock2 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[1]/a'
gainer_stock2_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[2]'
gainer_stock2_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[3]/span'
gainer_stock2_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[4]/span'
gainer_stock2_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[5]/span'

gainer_stock3 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[1]/a'
gainer_stock3_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[2]'
gainer_stock3_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[3]/span'
gainer_stock3_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[4]/span'
gainer_stock3_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[5]/span'

gainer_stock4 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[1]/a'
gainer_stock4_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[2]'
gainer_stock4_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[3]/span'
gainer_stock4_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[4]/span'
gainer_stock4_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[5]/span'

gainer_stock5 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[1]/a'
gainer_stock5_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[2]'
gainer_stock5_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[3]/span'
gainer_stock5_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[4]/span'
gainer_stock5_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[5]/span'

# Dispalys biggest losers
loser_stock1 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[1]/a'
loser_stock1_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[2]'
loser_stock1_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[3]/span'
loser_stock1_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[4]/span'
loser_stock1_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[1]/td[5]/span'

loser_stock2 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[1]/a'
loser_stock2_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[2]'
loser_stock2_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[3]/span'
loser_stock2_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[4]/span'
loser_stock2_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[2]/td[5]/span'

loser_stock3 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[1]/a'
loser_stock3_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[2]'
loser_stock3_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[3]/span'
loser_stock3_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[4]/span'
loser_stock3_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[3]/td[5]/span'

loser_stock4 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[1]/a'
loser_stock4_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[2]'
loser_stock4_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[3]/span'
loser_stock4_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[4]/span'
loser_stock4_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[4]/td[5]/span'

loser_stock5 = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[1]/a'
loser_stock5_name = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[2]'
loser_stock5_value = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[3]/span'
loser_stock5_change = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[4]/span'
loser_stock5_percent = '//*[@id="scr-res-table"]/div[1]/table/tbody/tr[5]/td[5]/span'