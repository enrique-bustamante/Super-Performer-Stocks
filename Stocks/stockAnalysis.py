# %%
# import dependencies
import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io

# %%
# Import the csv into a dataframe
stock_final = pd.read_csv('stockFinal.csv')

# %%
# Create a list of dates to use in loops
dateList = stock_final['Date'].unique().tolist()


# %%
# Create a list of alternative dates for today, 30, 60, and 20 day dates to avoid errors
dateToday = datetime.date.today()
date1 = (dateToday - datetime.timedelta(days=1)).isoformat()
date2 = (dateToday - datetime.timedelta(days=2)).isoformat()
date3 = (dateToday - datetime.timedelta(days=3)).isoformat()

date30 = (dateToday - datetime.timedelta(days=30)).isoformat()
date31 = (dateToday - datetime.timedelta(days=31)).isoformat()
date32 = (dateToday - datetime.timedelta(days=32)).isoformat()
date33 = (dateToday - datetime.timedelta(days=33)).isoformat()

date60 = (dateToday - datetime.timedelta(days=60)).isoformat()
date61 = (dateToday - datetime.timedelta(days=61)).isoformat()
date62 = (dateToday - datetime.timedelta(days=62)).isoformat()
date63 = (dateToday - datetime.timedelta(days=63)).isoformat()

date20 = (dateToday - datetime.timedelta(days=20)).isoformat()
date21 = (dateToday - datetime.timedelta(days=21)).isoformat()
date22 = (dateToday - datetime.timedelta(days=22)).isoformat()
date23 = (dateToday - datetime.timedelta(days=23)).isoformat()



# %%
# Adj date if the date is not in set
if dateToday in dateList:
    dateTodayString = dateToday.isoformat()
elif date1 in dateList:
    dateTodayString = date1
elif date2 in dateList:
    dateTodayString = date2
else:
    dateTodayString = date3

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

if date20  in dateList:
    date20Adj = date20
elif date21 in dateList:
    date20Adj = date21
elif date22 in dateList:
    date20Adj = date22
else:
    date20Adj = date23

# %%
# Get a count of how many days are under each stock name
#countDf = stock_final.groupby('Name', as_index=False).count()
#countDf = countDf[countDf['Open'] >= 60]

# %%
mainDf = stock_final[stock_final['Date'] == dateTodayString]
mainDf = mainDf.set_index('Name')
# %%
mainDf.rename(columns={'Close': 'Last_Price'}, inplace=True)

# %%
# Get the close at the 30 day mark and reduce columns
df30 = stock_final[stock_final['Date'] == date30Adj][['Name','200_MA']].set_index('Name')
df30.rename(columns={'200_MA': '200_30days'}, inplace=True)
# %%
# get the max and min close
dfMax = stock_final.groupby('Name')['Close'].max()
dfMin = stock_final.groupby('Name')['Close'].min()

# %%
# Merge 30 day, max, and min dfs into main
mainDf = mainDf.merge(df30, left_on='Name', right_on='Name')
mainDf = mainDf.merge(dfMax, left_on='Name', right_on='Name')
mainDf = mainDf.merge(dfMin, left_on='Name', right_on='Name')

# %%
# Drop unneeded columns and rename max and min columns to avoid confusion
mainDf = mainDf[['Last_Price', '200_MA','150_MA', '50_MA', '200_30days', 'Close_x', 'Close_y']]
mainDf.rename(columns={'Close_x': 'Close_max', 'Close_y': 'Close_min'}, inplace=True)

# %%
# Create list of names before any conditions are met. Will be needed for RS and RSI calculations
nameList = mainDf.index.tolist()

# %%
# Condition 1: The current price is greater than both the 150 and the 200 day moving average
mainDf['Cond1'] = (mainDf['Last_Price'] > mainDf['150_MA']) & (mainDf['Last_Price'] > mainDf['200_MA'])
mainDf = mainDf[mainDf['Cond1'] == True]

# Condition 2: The 150 day moving average is greater than the 200 day moving average
mainDf['Cond2'] = mainDf['150_MA'] > mainDf['200_MA']
mainDf = mainDf[mainDf['Cond2'] == True]

# Condition 3: The current 200 day moving average is greater than the 200 day moving average from 30 days ago
mainDf['Cond3'] = mainDf['200_MA'] > mainDf['200_30days']
mainDf = mainDf[mainDf['Cond3'] == True]

# Condition 4: The 50 day moving average is greater than the 150 moving average
mainDf['Cond4'] = mainDf['50_MA'] > mainDf['150_MA']
mainDf = mainDf[mainDf['Cond4'] == True]


# Condition 5: The current price is greater than the 50 day moving average
mainDf['Cond5'] = mainDf['Last_Price'] > mainDf['50_MA']
mainDf = mainDf[mainDf['Cond5'] == True]

# Condition 6: The current price is at least 30% than the 52 week low
mainDf['Cond6'] = mainDf['Last_Price'] > (mainDf['Close_min'] * 1.3)
mainDf = mainDf[mainDf['Cond6'] == True]

# Condition 7: The current price is at least within 70% of the 52 week high
mainDf['Cond7'] = mainDf['Last_Price'] > (0.75 * mainDf['Close_max'])
mainDf = mainDf[mainDf['Cond7'] == True]

# %%
# Create a dataframe for the last 20 days and include only companies in the nameList
last20DaysDf = stock_final[stock_final['Date'] >= date20Adj]
boolSeries = last20DaysDf.Name.isin(nameList)
last20DaysDf = last20DaysDf[boolSeries]

# %%
# Create the list of dates for the for loop to calculate RS and RSI
Dates20Days = last20DaysDf['Date'].unique().tolist()

# %%
# Create empty lists to store the up and down prices for the RS and RSI
upPrices = []
downPrices = []
counter = 0

# %%
# Run the for loop to cycle thought the names, for each date, to capture the price changes, either positive or negative
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
# Add the lists to the Last20DaysDf
last20DaysDf['Up'] = upPrices
last20DaysDf['Down'] = downPrices

# %%
# Create a dataframe to calculate the RS and TSI and merge these columns to the mainDf
relativeStrength = last20DaysDf.groupby('Name').mean()
relativeStrength = relativeStrength[['Up', 'Down']]
relativeStrength['RS'] = relativeStrength['Up']/relativeStrength['Down']
relativeStrength['RS Rank'] = relativeStrength['RS'].rank(pct=True)
relativeStrength['RSI'] = 100 - (100/(1 + relativeStrength['RS']))
mainDf = mainDf.merge(relativeStrength, left_on='Name', right_on='Name')

# %%
# Condition 8: Relative Strength ranking is in the 80th percentile
mainDf['Cond8'] = mainDf['RS Rank'] >= 0.80
mainDf = mainDf[mainDf['Cond8'] == True]

# %%
#mainDf['Pct Change 200 days'] = (mainDf['Last_Price'] - mainDf['200_MA'])/mainDf['200_MA']

# %%
mainDf['Cond9'] = mainDf['Pct Change 200 days'] >= 0.5
mainDf = mainDf[mainDf['Cond9'] == True]

# %%
#mainDf['Cond10'] = mainDf['RSI'] <= 70
#mainDf = mainDf[mainDf['Cond10'] == True]

# %%
# Create DF of oversold stocks
#overSold = relativeStrength[relativeStrength['RSI'] <= 30]
#overSoldList = overSold.index.to_list()

# %%
#overBought = mainDf[['RSI'] >= 70]
#overBoughtList = overBought.index.to_list()

# %%
# Reduce the columns in the Super performer list then save it as a csv
SPList = mainDf[[ 'Last_Price', 'RSI', 'Pct Change 200 days']]
SPList.to_csv('SPList.csv')
# %%
# read in the copy of SPList to compare to
copyDf = pd.read_csv('SPList copy.csv')
# Create empty lists and the main list to compare to
copyList = []
newToList = []
mainList = mainDf.index.to_list()

# %%
# Create for loop to see which stocks are new to the list
for name in mainList:
    if name not in copyList:
        newToList.append(name)


# Create for loop to see which teams are no longer meeting the conditions for a Super Performer
notOnListAnymore = []
for name in copyList:
    if name not in mainList:
        notOnListAnymore.append(name)

# %%
# Save a copy to use for the next time
SPList.to_csv('SPList copy.csv')

# %%
# %%
#overBoughtList.to_csv('Overbought.csv')
#overSoldList.to_csv('Oversold.csv')


# %%
