# %%
# import dependencies
import pandas as pd
from pandas.core.indexes.base import Index
from pandas.tseries.offsets import LastWeekOfMonth
import yfinance as yf
import datetime
import time
import requests
import io
import hvplot.pandas
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from plotly import express as px
import hvplot.pandas
from sklearn.cluster import KMeans
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html

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
# Add column for signal
stock_final['Signal EMA 50/200'] = 0.0
stock_final['Signal EMA 12/26'] = 0.0

# %%
# Set the signal to be 1 if it meets the condition
stock_final['Signal EMA 50/200'] = np.where(stock_final['50_EMA'] > stock_final['200_EMA'], 1.0, 0.0)
stock_final['Signal EMA 12/26'] = np.where(stock_final['12_EMA'] > stock_final['26_EMA'], 1.0, 0.0)

# %%
# define a function that cycles through each name and indicates the change in signal from the previous day(s)
def dailyDifference(df, column, days=1):
    grouped = df.groupby('Name')
    frames = []
    for group in grouped.groups:
        frame = grouped.get_group(group)
        frame['Entry/Exit'] = frame[column].diff(periods=days)
        frames.append(frame)
    tempDf = pd.concat(frames)
    return tempDf['Entry/Exit'].to_list()

# %%
stock_final['Entry/Exit 50/200'] = dailyDifference(stock_final, 'Signal EMA 50/200')
stock_final['Entry/Exit 12/26'] = dailyDifference(stock_final, 'Signal EMA 12/26')

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
#mainDf = mainDf[['Last_Price', '200_MA','150_MA', '50_MA', '200_30days', 'Close_x', 'Close_y', ]]
mainDf.rename(columns={'Close_x': 'Close_max', 'Close_y': 'Close_min'}, inplace=True)

# %%
# Create list of names before any conditions are met. Will be needed for RS and RSI calculations
nameList = mainDf.index.tolist()
stock_final = stock_final[stock_final.Name.isin(nameList)]

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
# Create empty lists to store the up and down prices for the RS and RSI
upPrices = []
downPrices = []
counter = 0

# %%
# Run the for loop to cycle thought the names, for each date, to capture the price changes, either positive or negative
for name in nameList:
    temp = stock_final[stock_final['Name'] == name]
    i = 0
    try:
        while i < len(dateList):
            if i == 0:
                upPrices.append(0)
                downPrices.append(0)
            else:
                if (temp.iloc[i,1] - temp.iloc[i-1, 1]) > 0:
                    temp1 = temp.iloc[i,1] - temp.iloc[i-1, 1]
                    upPrices.append(temp1)
                    downPrices.append(0)
                else:
                    temp1 = temp.iloc[i-1, 1] - temp.iloc[i,1]
                    upPrices.append(0)
                    downPrices.append(temp1)
            i += 1
    except:
        pass
    counter += 1

# %%
# Add the lists to the Last20DaysDf
stock_final['Up'] = upPrices
stock_final['Down'] = downPrices

# %%
# Calculate the 14 day moving average for the ups and downs
def movingAverage(df,column, spanDays):
    listMA = df.groupby('Name')[column].rolling(window=spanDays, min_periods=1).mean().to_list()
    return listMA

stock_final['Up_MA'] = movingAverage(stock_final,'Up', 14)
stock_final['Down_MA'] = movingAverage(stock_final, 'Down', 14)

# %%
#
stock_final['RS'] = stock_final['Up_MA']/stock_final['Down_MA']
stock_final['RSI'] = 100 - (100/(1 + stock_final['RS']))

# %%
stock_final['Signal RSI'] = np.where(stock_final['RSI'] > 70, 1.0, 0.0)
stock_final['Entry/Exit RSI'] = dailyDifference(stock_final, 'Signal RSI')

# %%
stock_final['RSI ROC'] = dailyDifference(stock_final, 'RSI', 3)
stock_final['RSI ROC'] = stock_final['RSI ROC']/3
# %%
# Create a dataframe for the last 20 days and include only companies in the nameList
last20DaysDf = stock_final[stock_final['Date'] >= date20Adj]
last20DaysDf = last20DaysDf[last20DaysDf.Name.isin(nameList)]

# %%
# Create the list of dates for the for loop to calculate RS and RSI
Dates20Days = last20DaysDf['Date'].unique().tolist()

# %%
# Create a dataframe to calculate the RS and TSI and merge these columns to the mainDf
dayOfDf = last20DaysDf[last20DaysDf['Date'] == dateTodayString]
dayOfDf = dayOfDf[['Name', 'RS', 'Signal RSI', 'Entry/Exit RSI', 'RSI ROC']]
dayOfDf['RS Rank'] = dayOfDf['RS'].rank(pct=True)
dayOfDf = dayOfDf[['Name', 'RS Rank', 'Signal RSI', 'Entry/Exit RSI', 'RSI ROC']]
mainDf = mainDf.merge(dayOfDf, left_on='Name', right_on='Name')

#for name in nameList:
#    temp = last20DayDf[last20DayDf['Name'] == name]
#    i = 0
#    try:
#        while i < len(Dates20Days):
#            if i == 0:
#                upPrices.append(0)
#                downPrices.append(0)
#            else:
#                if (temp.iloc[i,4] - temp.iloc[i-1, 4]) > 0:
#                    temp1 = temp.iloc[i,4] - temp.iloc[i-1, 4]
#                    upPrices.append(temp1)
#                    downPrices.append(0)
#                else:
#                    temp1 = temp.iloc[i-1, 4] - temp.iloc[i,4]
#                    upPrices.append(0)
#                    downPrices.append(temp1)
#            i += 1
#    except:
#        pass
#    counter += 1
#    print (temp)
#    print (temp1)

# %%
# Condition 8: Relative Strength ranking is in the 80th percentile
mainDf['Cond8'] = mainDf['RS Rank'] >= 0.90
mainDf = mainDf[mainDf['Cond8'] == True]

# %%
# Calculate the Stochastic Oscillator max and min values
stochasticMaxDf = last20DaysDf.groupby('Name').max()
stochasticMaxDf.rename(columns={'Close': 'Stoch Max'}, inplace=True)
stochasticMaxDf = stochasticMaxDf[['Stoch Max']]

stochasticMinDf = last20DaysDf.groupby('Name').min()
stochasticMinDf.rename(columns={'Close': 'Stoch Min'}, inplace=True)
stochasticMinDf = stochasticMinDf[['Stoch Min']]

# %%
mainDf = mainDf.merge(stochasticMaxDf, left_on='Name', right_on='Name')
mainDf = mainDf.merge(stochasticMinDf, left_on='Name', right_on='Name')

# %%
# Calculate stochastic oscillator
last20DaysDf = last20DaysDf.merge(stochasticMaxDf, how='left', left_on='Name', right_on='Name')
last20DaysDf = last20DaysDf.merge(stochasticMinDf, how='left', left_on='Name', right_on='Name')
# %%
last20DaysDf['K%'] = ((last20DaysDf['Close'] - last20DaysDf['Stoch Min'])/(last20DaysDf['Stoch Max'] - last20DaysDf['Stoch Min'])) * 100

# %%
rolling3DayMean = last20DaysDf.groupby('Name')['K%'].rolling(window=3, min_periods=1).mean()

# %%
#mainDf['Pct Change 200 days'] = (mainDf['Last_Price'] - mainDf['200_MA'])/mainDf['200_MA']
rollingList = rolling3DayMean.to_list()
last20DaysDf['D%'] = rollingList

# %%
# Set up signals and entry/exit point columns
last20DaysDf['Signal K%'] = np.where(last20DaysDf['K%'] > last20DaysDf['D%'], 1.0, 0.0)
last20DaysDf['Entry/Exit K%'] = dailyDifference(last20DaysDf,'Signal K%')
last20DaysDf['K ROC'] = dailyDifference(last20DaysDf, 'K%', 3)
last20DaysDf['K ROC'] = last20DaysDf['K ROC']/3

# %%
# Merge %k signal and entry/exit columns to main
todayDf = last20DaysDf[last20DaysDf['Date'] == dateTodayString]
todayDf = todayDf[['Name', 'K%', 'Signal K%', 'Entry/Exit K%', 'K ROC']]
mainDf = mainDf.merge(todayDf, how='left', left_on='Name', right_on='Name')

# %%
machLearnDf = mainDf.drop(columns=['Name', 'Date', 'Cond1', 'Cond2', 'Cond3', 'Cond4', 'Cond5', 'Cond6', 'Cond7', 'Cond8'])
mainDf = mainDf[['Name', 'Last_Price', 'Signal EMA 50/200', 'Entry/Exit 50/200', 'Signal EMA 12/26', 'Entry/Exit 12/26', 'Signal RSI', 'Entry/Exit RSI','RSI ROC', 'Signal K%', 'Entry/Exit K%','K ROC']]
MachLearnNames = pd.DataFrame(mainDf['Name'], index=mainDf.index)
# %%
notTradedRHList = ['AAIT','CYCCP', 'DXLG','SIBC', 'SONA', 'STLY', 'WHLRP']

# %%
traded = []
for i in mainDf['Name']:
    if i not in notTradedRHList:
        traded.append(True)
    else:
        traded.append(False)

# %%
mainDf['Traded'] = traded


# %%
owned = ['ATRC', 'BECN', 'BGFV', 'CAKE', 'DCOM', 'FOXF', 'GIII', 'GTLS', 'GT', 'HCCI', 'IMKTA', 'KFRC', 'KIRK', 'LPLA', 'SASR', 'SBNY', 'STAA', 'TACT', 'TBBK', 'TOWN']

# %%
mainDf = mainDf.set_index('Name')

# %%
sumDf = mainDf.drop(columns=['Last_Price', 'Traded'])


# %%
status = []
for name in sumDf.index:

    if ((sumDf.loc[name]['Signal EMA 50/200'] == 1) or (sumDf.loc[name]['Signal EMA 12/26'] == 1)) and ((sumDf.loc[name]['Entry/Exit RSI'] == 0) and (sumDf.loc[name]['Entry/Exit K%'] == 0)) and ((sumDf.loc[name]['RSI ROC'] > 0) and (sumDf.loc[name]['K ROC'] > 0)) and ((sumDf.loc[name]['Signal RSI'] == 0) or (sumDf.loc[name]['Signal K%'] == 0)):
        status.append('Buy')
    elif (sumDf.loc[name]['Entry/Exit RSI'] == -1) or (sumDf.loc[name]['Entry/Exit K%'] == -1) or (((sumDf.loc[name]['RSI ROC'] < 0) and (sumDf.loc[name]['K ROC'] < 0))  and ((sumDf.loc[name]['Signal RSI'] == 0) or (sumDf.loc[name]['Signal K%'] == 0))):
        status.append('Sell')
    elif (sumDf.loc[name]['RSI ROC'] > 0) or (sumDf.loc[name]['K ROC'] > 0):
        status.append('Potential buy')
    else:
        status.append('Hold')

# %%
mainDf['Status'] = status


# %% [markdown]
### Machine Learning

# %%
# Scale and standardize data
mLScaledArray = StandardScaler().fit_transform(machLearnDf)

# %%
# Find the best number of components for PCA
pcaTrial = PCA(n_components=25)
principalComponents = pcaTrial.fit_transform(mLScaledArray)

# %%
features = range(pcaTrial.n_components_)
variance = pcaTrial.explained_variance_ratio_
compData = {'Components': features, 'Variance': variance}
compDf = pd.DataFrame(compData)
compDf.hvplot.bar(x='Components', y='Variance', title='Component Variance', xticks='Components', color='blue')

# %%
# reduce to principle components using PCA
pca = PCA(n_components=3)
pcaDf = pca.fit_transform(mLScaledArray)

# %% [markdown]
#### Cluster Model

# %%
inertia = []
k = list(range(1,11))
for i in k:
    km = KMeans(n_clusters=i, random_state=42)
    km.fit(pcaDf)
    inertia.append(km.inertia_)

# %%
# Create chart to see elbow curve
elbow_data = {"k": k, "inertia": inertia}
df_elbow = pd.DataFrame(elbow_data)
df_elbow.hvplot.line(x="k", y="inertia", title="Elbow Curve", xticks=k)

# %%
km = KMeans(n_clusters=4, random_state=42)
km.fit(pcaDf)
prediction = km.predict(pcaDf)

# %%
clustered = pd.DataFrame({'Name': MachLearnNames['Name'], 'Last Price': machLearnDf['Last_Price'],'PC1': pcaDf[:,0], 'PC2': pcaDf[:,1], 'PC3': pcaDf[:,2], 'Class': km.labels_})
km.labels_
pcaDf[:,0]

# %% [markdown]
### Visualization

# %%
fig = px.scatter_3d(
    clustered,
    x='PC1',
    y='PC2',
    z='PC3',
    color='Class',
    symbol='Class',
    hover_name='Name',
    hover_data=['Last Price']
)
fig.update_layout(legend=dict(x=0, y=1))
fig.show()

# %%
fig1 = make_subplots(
    rows=4,
    cols=1,
    specs=[[{'type': 'candlestick'}], [{'type': 'candlestick'}], [{'type': 'candlestick'}], [{'type': 'candlestick'}]]
)
# %%
df = stock_final[stock_final['Name'] == 'TRNS']
# %%
fig1.add_trace(go.Figure(data=[go.Candlestick(x=df['Date'])]))


# %%
#app = dash.Dash(__name__)
#app.layout = html.Div([
#    dcc.Graph(figure=fig)
#])

#app.run_server(debug=True, use_reloader=True)


# %% [markdown]
### Outputs

# %%
buyDf = mainDf[mainDf['Status'] == 'Buy']
buyList = []
for name in buyDf.index:
    if name not in owned:
        buyList.append(name)

ownedDf = mainDf[mainDf.index.isin(owned)]

# %%
sellDf = mainDf[mainDf['Status'] == 'Sell']
sellList = []
for name in sellDf.index:
    if name in owned:
        sellList.append(name)
for name in owned:
    if name not in mainDf.index:
        sellList.append(name)

# %%
# Reduce the columns in the Super performer list then save it as a csv
#SPList = mainDf[[ 'Last_Price', 'RSI']]
SPList.to_csv('SPList.csv')
# %%
# read in the copy of SPList to compare to
copyDf = pd.read_csv('SPList copy.csv')
# Create empty lists and the main list to compare to
copyList = []
newToList = []
mainList = mainDf.index.to_list()

# %%
# Save a copy to use for the next time
SPList.to_csv('SPList copy.csv')

# %%
# %%
#overBoughtList.to_csv('Overbought.csv')
#overSoldList.to_csv('Oversold.csv')


# %%
