def zScore(df):
    ''' Calculate the mean and standard deviation to find the Z-score by passing dataframe through this function'''
    dfValueMean = df['value'].mean()
    dfValueSTD = df['value'].std()
    dfProjMean = df['projection'].mean()
    dfProjSTD = df['projection'].std()
    dfFormMean = df['form'].mean()
    dfFormSTD = df['form'].std()
    dfPointsMean = df['total_points'].mean()
    dfPointsSTD = df['total_points'].mean()
    zScoreValue = (df.loc[:,'value'] - dfValueMean)/dfValueSTD
    zScoreProjection = (df.loc[:,'projection'] - dfProjMean)/dfProjSTD
    zScoreForm = (df.loc[:,'form'] - dfFormMean)/dfFormSTD
    zScorePoints = (df.loc[:,'total_points'] - dfFormMean)/dfFormSTD
    df['Z Score'] = 2*zScoreValue + 2*zScoreProjection + zScoreForm + 2*zScorePoints
    return df

def columnsAsType(df, listOfColumns, type):
    ''' pass a list of columns and convert them to specified type '''
    for n in listOfColumns:
        df[n] = df[n].astype(type)


def positionDf(df, position):
    df = df[df['position'] == position]
    return df

def rankDf(df, columnCreatedName, columnBeingRanked):
    df[columnCreatedName] = df[columnBeingRanked].rank(ascending=False)
    df = df.sort_values(columnCreatedName)
    return df


