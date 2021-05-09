# %%
# import dependencies
import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io

# %%
stock_final = pd.read_csv('stockFinal.csv')

# %%
dateList = stock_final['Date'].unique().tolist()


# %%
dateToday = datetime.date.today()
date1 = (dateToday - datetime.timedelta(days=1)).isoformat()
date2 = (dateToday - datetime.timedelta(days=2)).isoformat()
date3 = (dateToday - datetime.timedelta(days=3)).isoformat()
if dateToday in dateList:
    dateTodayString = dateToday.isoformat()
elif date1 in dateList:
    dateTodayString = date1
elif date2 in dateList:
    dateTodayString = date2
else:
    dateTodayString = date3


date30 = (dateToday - datetime.timedelta(days=30)).isoformat()
date31 = (dateToday - datetime.timedelta(days=31)).isoformat()
date32 = (dateToday - datetime.timedelta(days=32)).isoformat()
date33 = (dateToday - datetime.timedelta(days=33)).isoformat()
date60 = (dateToday - datetime.timedelta(days=60)).isoformat()
date61 = (dateToday - datetime.timedelta(days=61)).isoformat()
date62 = (dateToday - datetime.timedelta(days=62)).isoformat()
date63 = (dateToday - datetime.timedelta(days=63)).isoformat()



# %%
# Adj date if the date is not in set
if date30  in dateList:
    date30Adj = date30
elif date31 in dateList:
    date30Adj = date31
elif date32 in dateList:
    date30Adj = date32
else:
    date30Adj = date33

if date60  in dateList:
    date60Adj = date60
elif date61 in dateList:
    date60Adj = date61
elif date32 in dateList:
    date60Adj = date62
else:
    date60Adj = date63

# %%
countDf = stock_final.groupby('Name', as_index=False).count()
countDf = countDf[countDf['Open'] >= 60]

# %%
mainDf = stock_final[stock_final['Date'] == dateTodayString]
mainDf = mainDf.set_index('Name')
# %%
mainDf.rename(columns={'Close': 'Last_Price'}, inplace=True)

# %%
# Get the close at the 30 day mark
df30 = stock_final[stock_final['Date'] == date30Adj][['Name','200_MA']].set_index('Name')
# %%
df30.rename(columns={'200_MA': '200_30days'}, inplace=True)
# %%
# get the close at the 60 day mark
dfMax = stock_final.groupby('Name')['Close'].max()

# %%
dfMin = stock_final.groupby('Name')['Close'].min()

# %%
# Merge dfs
mainDf = mainDf.merge(df30, left_on='Name', right_on='Name')
# %%
mainDf = mainDf.merge(dfMax, left_on='Name', right_on='Name')
mainDf = mainDf.merge(dfMin, left_on='Name', right_on='Name')

# %%
# Drop unneeded columns
mainDf = mainDf[['Last_Price', '200_MA','150_MA', '50_MA', '200_30days', 'Close_x', 'Close_y']]


# %%
mainDf.rename(columns={'Close_x': 'Close_max', 'Close_y': 'Close_min'}, inplace=True)

# %%
nameList = mainDf.index.tolist()

# %%
mainDf['Cond1'] = (mainDf['Last_Price'] > mainDf['150_MA']) & (mainDf['Last_Price'] > mainDf['200_MA'])
mainDf = mainDf[mainDf['Cond1'] == True]
# %%
mainDf['Cond2'] = mainDf['150_MA'] > mainDf['200_MA']
mainDf = mainDf[mainDf['Cond2'] == True]

# %%
mainDf['Cond3'] = mainDf['200_MA'] > mainDf['200_30days']
mainDf = mainDf[mainDf['Cond3'] == True]

# %%
mainDf['Cond4'] = mainDf['50_MA'] > mainDf['150_MA']
mainDf = mainDf[mainDf['Cond4'] == True]


# %%
mainDf['Cond5'] = mainDf['Last_Price'] > mainDf['50_MA']
mainDf = mainDf[mainDf['Cond5'] == True]
# %%
mainDf['Cond6'] = mainDf['Last_Price'] > (mainDf['Close_min'] * 1.3)
mainDf = mainDf[mainDf['Cond6'] == True]
# %%
mainDf['Cond7'] = mainDf['Last_Price'] > (0.75 * mainDf['Close_max'])
mainDf = mainDf[mainDf['Cond7'] == True]
# %%
date20 = (dateToday - datetime.timedelta(days=20)).isoformat()
date21 = (dateToday - datetime.timedelta(days=21)).isoformat()
date22 = (dateToday - datetime.timedelta(days=22)).isoformat()
date23 = (dateToday - datetime.timedelta(days=23)).isoformat()

if date20  in dateList:
    date20Adj = date20
elif date21 in dateList:
    date20Adj = date21
elif date22 in dateList:
    date20Adj = date22
else:
    date20Adj = date23

# %%
last20DaysDf = stock_final[stock_final['Date'] >= date20Adj]

# %%
boolSeries = last20DaysDf.Name.isin(nameList)
last20DaysDf = last20DaysDf[boolSeries]

# %%
#AAL = last20DaysDf[last20DaysDf['Name'] == 'AAL']
Dates20Days = last20DaysDf['Date'].unique().tolist()

# %%

upPrices = []
downPrices = []
nameList1 = ['AAL', 'AAPL']

# %%
counter = 0

# %%
for name in nameList:
    temp = last20DaysDf[last20DaysDf['Name'] == name]
    i = 0
    try:
        while i < len(Dates20Days):
            if i == 0:
                upPrices.append(0)
                downPrices.append(0)
            else:
                if (temp.iloc[i,4] - temp.iloc[i-1, 4]) > 0:
                    temp1 = temp.iloc[i,4] - temp.iloc[i-1, 4]
                    upPrices.append(temp1)
                    downPrices.append(0)
                else:
                    temp1 = temp.iloc[i-1, 4] - temp.iloc[i,4]
                    upPrices.append(0)
                    downPrices.append(temp1)
            i += 1
    except:
        pass
    counter += 1
    print (temp)
    print (temp1)
# %%
last20DaysDf['Up'] = upPrices
last20DaysDf['Down'] = downPrices
# %%
relativeStrength = last20DaysDf.groupby('Name').mean()

# %%
relativeStrength = relativeStrength[['Up', 'Down']]
# %%
relativeStrength['RS'] = relativeStrength['Up']/relativeStrength['Down']
# %%
relativeStrength['RS Rank'] = relativeStrength['RS'].rank(pct=True)
# %%
relativeStrength['RSI'] = 100 - (100/(1 + relativeStrength['RS']))
# %%
mainDf = mainDf.merge(relativeStrength, left_on='Name', right_on='Name')
# %%
# Condition 8: Relative Strength risk greater than 80%
mainDf['Cond8'] = mainDf['RS Rank'] >= 0.80
mainDf = mainDf[mainDf['Cond8'] == True]
# %%
# Create DF of oversold stocks
overSold = relativeStrength[relativeStrength['RSI'] <= 30]

# %%
overBought = mainDf[mainDf['RSI'] >= 70]
# %%
SPList = mainDf[[ 'Last_Price']]
# %%
SPList.to_csv('SPList.csv')
# %%
copyDf = pd.read_csv('SPList copy.csv')
# %%
copyList = []
# %%
newToList = []
mainList = mainDf.index.to_list()

# %%
for name in mainList:
    if name not in copyList:
        newToList.append(name)

# %%
newDict = {'Name': newToList}
newToListDf = pd.DataFrame(newDict)
newToListDf.to_csv('newToList.csv')

# %%
notOnListAnymore = []
for name in copyList:
    if name not in mainList:
        notOnListAnymore.append(name)

noLongerDf = pd.DataFrame({'Name': notOnListAnymore})
noLongerDf.to_csv('noLongerOnList.csv')
# %%
SPList.to_csv('SPList copy.csv')
