def zScore(df):
    ''' Calculate the mean and standard deviation to find the Z-score by passing dataframe through this function'''
    dfValueMean = df['value'].mean()
    dfValueSTD = df['value'].std()
    dfProjMean = df['projection'].mean()
    dfProjSTD = df['projection'].std()
    dfFormMean = df['form'].mean()
    dfFormSTD = df['form'].std()
    zScoreValue = (df.loc[:,'value'] - dfValueMean)/dfValueSTD
    zScoreProjection = (df.loc[:,'projection'] - dfProjMean)/dfProjSTD
    zScoreForm = (df.loc[:,'form'] - dfFormMean)/dfFormSTD
    df['Z Score'] = 2*zScoreValue + 2*zScoreProjection + zScoreForm
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


