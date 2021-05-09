# %%
# import dependencies
import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io

# %%
# set date range
start = datetime.date.today() - datetime.timedelta(days=260)
end = datetime.date.today()

# %%
# Get stock ticker symbols
url="https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"
s = requests.get(url).content
companies = pd.read_csv(io.StringIO(s.decode('utf-8')))

# %%
# create list of symbols
symbols = companies['Symbol'].to_list()

# %%
stock_final = pd.DataFrame()
# %%
# iterate over each symbol
for i in symbols:
    print(str(symbols.index(i)) + str(' : ') + i, sep=',', end=',', flush=True)
    try:
        #download stock price
        stock = []
        stock = yf.download(i, start=start, end=end, progress=False)

        # append the individual stock prices
        if len(stock) == 0:
            None
        else:
            stock['Name']=i
            stock_final = stock_final.append(stock, sort=False)

    except Exception:
        None

stock_final.head()

# %%
# create rolling averages
stock_final['200_MA'] = stock_final['Close'].rolling(window=200).mean()
stock_final['150_MA'] = stock_final['Close'].rolling(window=150).mean()
stock_final['50_MA'] = stock_final['Close'].rolling(window=50).mean()

# %%
stock_final = stock_final.dropna()

# %%
stock_final.to_csv('stockFinal.csv')


# %%
