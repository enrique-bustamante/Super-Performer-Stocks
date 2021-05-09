# %%
# import dependencies
import requests
import pandas as pd
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
import numpy as np

# %%
# set up tickers
tickers = si.tickers_sp500()
recommendations = []

for ticker in tickers:
    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'

    url = lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        recommendation = 6
    try:
        result = r.json()['quoteSummary']['result'][0]
        recommendation = result['financialData']['recommendationMean']['fmt']
    except:
        recommendation = 6

    recommendations.append(recommendation)
    print("-------------------------")
    print("{} has an average recommendation of: ".format(ticker), recommendation)
    #time.sleep(0.5)

# %%
# Create dataframe
df = pd.DataFrame(list(zip(tickers, recommendations)), columns = ['Company', 'Recommendations'])
df = df.set_index('Company')
df.to_csv('recommendations.csv')
print (df)

# %%
fullList = []
for ticker in tickers:
    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'
    url = lhs_url + ticker + rhs_url
    r = requests.get(url)
    result = r.json()
    print(result)
    fullList.append(result)

# %%
