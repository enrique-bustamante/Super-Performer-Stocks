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
start = datetime.date.today() - datetime.timedelta(days=365)
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
def movingAverage(df, spanDays):
    listMA = df.groupby('Name')['Close'].rolling(window=spanDays, min_periods=1).mean().to_list()
    return listMA

# %%
stock_final['200_MA'] = movingAverage(stock_final, 200)
stock_final['150_MA'] = movingAverage(stock_final, 150)
stock_final['50_MA'] = movingAverage(stock_final, 50)

# create rolling averages
#list200 = stock_final.groupby('Name')['Close'].rolling(window=200, min_periods=1).mean().to_list()
#stock_final['200_MA'] = list200

#list150 = stock_final.groupby('Name')['Close'].rolling(window=150, min_periods=1).mean().to_list()
#stock_final['150_MA'] = list150

#list50 = stock_final.groupby('Name')['Close'].rolling(window=50, min_periods=1).mean().to_list()
#stock_final['50_MA'] = list50

# %%
def emaColumn(df,spanDays):
    grouped = df.groupby('Name')
    frames = []
    for group in grouped.groups:
        frame = grouped.get_group(group)
        frame['EMA'] = frame['Close'].ewm(span=spanDays, min_periods=1).mean()
        frames.append(frame)
    tempDf = pd.concat(frames)
    return tempDf['EMA'].to_list()

# %%
stock_final['200_EMA'] = emaColumn(stock_final, 200)
stock_final['50_EMA'] = emaColumn(stock_final, 50)
stock_final['26_EMA'] = emaColumn(stock_final, 26)
stock_final['12_EMA'] = emaColumn(stock_final, 12)

# %%
# drop NAs
stock_final = stock_final.dropna()

# %%
# Drop unnecessary columns
stock_final = stock_final.drop(columns=['Adj Close', 'Volume'])

# %%
stock_final.to_csv('stockFinal.csv')


# %%
