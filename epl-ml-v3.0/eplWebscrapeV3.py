# %%
# Import dependencies

# Import basic libraries
import pandas as pd
import numpy as np # might not be used after all

# Import visualization libraries
from IPython.display import HTML
import matplotlib.pyplot as plt
import seaborn as sns
import dataframe_image as dfi

# Import preprocessing libraries
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Import machine learning libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

# Import metrics libraries
from sklearn.metrics import r2_score

# Import webscraping libraries
import requests
from bs4 import BeautifulSoup as soup

# Import functions
from myFunctions import *
# %%
# Set up the connection to the API for download
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json = r.json()

# %%
# Create the dataframes that will be combined into our main dataframe
elementsDf = pd.DataFrame(json['elements'])
elementTypesDf = pd.DataFrame(json['element_types'])
teamsDf = pd.DataFrame(json['teams'])

# %%
# Run a transpose of the df to see all fields
trans = elementsDf.T

# %%
# delete the transposed df from the IDE
del trans
del json

# %%
# Combine columns from dataframes into main
elementsDf['position'] = elementsDf.element_type.map(elementTypesDf.set_index('id').singular_name)
elementsDf['team'] = elementsDf.team.map(teamsDf.set_index('id').name)

# Make needed calculations and adjustments to the data
elementsDf['now_cost'] = elementsDf['now_cost']/10 # cost is multiplied by 10 for some reason in the original data set
elementsDf['value'] = elementsDf['total_points']/elementsDf['now_cost']
#elementColumns = elementsDf.columns might not need this

# %%
# Convert data into floats
columnsList = ['form', 'points_per_game', 'ict_index']
columnsAsType(elementsDf, columnsList, float)

# %%
# Reduce the main dataframe to the necessary columns and set index
elementsDf = elementsDf[['web_name', 'team', 'position', 'form','points_per_game', 'now_cost', 'minutes','goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'bonus', 'ict_index', 'total_points', 'value']]
elementsDf.set_index(['web_name'])

# %%
# Calculate the minutes cutoff
gameweek = int(input('Gameweek that just ended: '))
elementsDf = elementsDf[elementsDf['minutes'] >= (60 * gameweek)]
del gameweek

# %% [markdown]
# Machine Learning

# %%
# Separate the dataframe into categorical and numerical values
categoricalDf = elementsDf[['web_name', 'team', 'position','value', 'form', 'now_cost', 'total_points']].set_index(['web_name'])
numericalDf = elementsDf.drop(columns=['team', 'position', 'form', 'now_cost']).set_index(['web_name'])

# %%
# Split data into training and test sets
numericalAttributes = numericalDf.drop(['value'], axis=1)
numericalFeatures = numericalDf['value']
numericTrainAttributes, numericTestAttributes, numericTrainFeatures, numericTestFeatures = train_test_split(numericalAttributes, numericalFeatures, test_size=0.2, random_state=42)

# %%
# Standardize the numerical data
scaler = StandardScaler()
trainScaled = scaler.fit_transform(numericTrainAttributes)
testScaled = scaler.transform(numericTestAttributes)

# %%
# Fine tune mode using GridSearchCV
parameters = {'n_estimators': [50, 100, 150, 200]}

search = GridSearchCV(RandomForestRegressor(), param_grid=parameters, cv=5)
search.fit(trainScaled, numericTrainFeatures)
bestParam = search.best_params_.get('n_estimators')

rfModel = RandomForestRegressor(n_estimators=bestParam)
rfModel.fit(trainScaled, numericTrainFeatures)
yPred = rfModel.predict(testScaled)

# %%
# Test accuracy of model
r2_score(numericTestFeatures, yPred)

# %%
# Run data through model and add prediction column
categoricalDf['predicted_value'] = rfModel.predict(scaler.transform(numericalAttributes))
categoricalDf['projection'] = categoricalDf['predicted_value'] * categoricalDf['now_cost']

# %%
# Clean up workspace
del numericalAttributes
del numericalFeatures
del numericTestAttributes
del numericTestFeatures
del numericTrainAttributes
del numericTrainFeatures
del parameters
del rfModel
del scaler
del search
del testScaled
del trainScaled
del yPred

# %%
# Calculate all positions z-score
categoricalDfZ = zScore(categoricalDf)
categoricalDf['All position Z score'] = categoricalDfZ['Z Score']

# %%
# Separate data into positional dataframes
defenderDf = positionDf(categoricalDf, 'Defender')
goalieDf = positionDf(categoricalDf, 'Goalkeeper')
middieDf = positionDf(categoricalDf, 'Midfielder')
forwardDf = positionDf(categoricalDf, 'Forward')

# %%
# Calculate the positional z-score for all dfs
defenderDf = zScore(defenderDf)
goalieDf = zScore(goalieDf)
middieDf = zScore(middieDf)
forwardDf = zScore(forwardDf)

# %%
# Calculate combined total and positional z-score
defenderDf['Final Z Score'] = defenderDf['All position Z score'] + defenderDf['Z Score']
goalieDf['Final Z Score'] = goalieDf['All position Z score'] + goalieDf['Z Score']
middieDf['Final Z Score'] = middieDf['All position Z score'] + middieDf['Z Score']
forwardDf['Final Z Score'] = forwardDf['All position Z score'] + forwardDf['Z Score']

# %%
# Rank the dfs by final z-score
defenderDf = rankDf(defenderDf, 'Total rank', 'Final Z Score')
goalieDf = rankDf(goalieDf, 'Total rank', 'Final Z Score')
middieDf = rankDf(middieDf, 'Total rank', 'Final Z Score')
forwardDf = rankDf(forwardDf, 'Total rank', 'Final Z Score')

# %%
# Filter dfs to the essential columns
columnsList = ['team', 'position', 'value', 'projection', 'now_cost', 'Total rank', 'form', 'total_points']
defenderDf = defenderDf[columnsList]
goalieDf = goalieDf[columnsList]
middieDf = middieDf[columnsList]
forwardDf = forwardDf[columnsList]

# %%
# Save top 20 of each position as html
HTML(defenderDf.head(20).to_html('templates/defenders.html', classes='table table-striped'))
HTML(goalieDf.head(20).to_html('templates/goalies.html', classes='table table-striped'))
HTML(middieDf.head(20).to_html('templates/midfielders.html', classes='table table-striped'))
HTML(forwardDf.head(20).to_html('templates/forwards.html', classes='table table-striped'))

# %%
dfi.export(defenderDf.head(20),'images/defenders.png')
dfi.export(goalieDf.head(20),'images/goalies.png')
dfi.export(middieDf.head(20),'images/midfielders.png')
dfi.export(forwardDf.head(20),'images/forwards.png')


# %%
# save dataframes to csvs
defenderDf.to_csv('rankings/DefenderRank.csv',index=True)
goalieDf.to_csv('rankings/GoalieRank.csv', index=True)
middieDf.to_csv('rankings/MidfielderRank.csv', index=True)
forwardDf.to_csv('rankings/ForwardRank.csv',index=True)

# %%
# Visualization
sns.relplot(data=elementsDf, x='now_cost', y='points_per_game', col='position', hue='bonus', col_wrap=2)
plt.savefig('images/costVsPPG.png')


# %%
sns.displot(elementsDf,x='points_per_game', hue='position', kind='kde', fill=True)
plt.savefig('images/ppg.png')

# %%
sns.boxplot(data=elementsDf, y='points_per_game', x='position')
plt.savefig('images/ppgBox.png')
# %%
sns.displot(elementsDf, x='ict_index', hue='position', kind='kde', fill=True)
plt.savefig('images/ictIndex.png')

# %%
sns.displot(elementsDf, x='bonus', hue='position', kind='kde', fill=True)
plt.savefig('images/bonus.png')

# %%
sns.displot(elementsDf, x='form', hue='position', kind='kde', fill=True)
plt.savefig('images/form.png')

# %%
sns.displot(elementsDf, x='total_points', hue='position', kind='kde', fill=True)
plt.savefig('images/points.png')