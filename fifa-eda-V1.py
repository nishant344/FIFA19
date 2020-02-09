from zipfile import ZipFile
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # matplotlib for plotting
import seaborn as sns # seaborn for better graphics

# Check if csv file is already extracted from zip file in data folder, if not extracted, extract zip file        
if any(os.path.splitext(f)[1] == '.csv' for f in os.listdir('./data')) == False:
    with ZipFile("data/fifa19.zip","r") as zip_ref:
        zip_ref.extractall("data")
        print("data extracted")
else:
    print("csv file already present")
# now csv file is extracted

df=pd.read_csv('./data/data.csv')

print(df.shape)
# We can see the total number of data entries to be 18207

# Check the info of data to analyse columns and null values
df.info()

# We can see data has first column as "Unnamed" and it look to be index. Lets set it as index.
df=df.set_index(df.columns[0])
# Lets remove the index name as it doesn't make sense
del df.index.name
df.head()
# Total of 88 columns availbale. Not all relevant to everyone.
df.columns

# Lets remove the columns that are not useful for our analysis.
cols_remove=['Photo','Flag','Club Logo','Real Face','Jersey Number']
df=df.drop(cols_remove,axis=1)

# Find occurances of null values in each columns
df_null_count=df.isna().sum()
# There are 9 columns with no null values, so lets remove them from our null value analysis.
df_null_count=df_null_count[df_null_count>0]
# columns with null values
df_null_cols=list(df_null_count.index)
df_null_cols=[x.replace(' ','_') for x in df_null_cols]

# Lets tackle null values in these remaining columns and understand them

# Analysing df_null_count, we can see there are 241 players with no club. Let's assume these are potential players for clubs to purchase.
# For now lets separate them to a new data frame and remove them from our main dataset (df)
df_noclub=df[df.Club.isnull()]
df=df.dropna(subset=['Club'])
df=df.reset_index(drop=True)

# Goal keeps dont have attributes such as LS, ST, RS, etc attribute. Hence they all have null values in them.
# So lets create another dataframe for position='GK'.
# In future analysis when all players are analyses together, we dont considered such columns.
df_GK=df[df['Position']=='GK']

# Anlysing null values in Preferred Foot Column
df_PF_null=df[df['Preferred Foot'].isnull()]
# Analysing this, we see there are 48 such players and all have potential of 62.
# They have no data relevent to their positional skills and physical attributes. We can remove them.
# This will remove null values in many columns which we will see next.
df=df.dropna(subset=['Preferred Foot'])
df=df.reset_index(drop=True)
del df_PF_null

# Lets check null values again
df_null_count=df.isna().sum()
df_null_count=df_null_count[df_null_count>0]
# Now alanlysing the remaining pattern of null values, there is a logical pattern.
# If a player is loaned from a club, its 'Joined' and 'Release Clause' column is logically blank.
# This is verfied by counting total of null values in 'Loaned From' and 'Joined' column which sums up to total data points.
# Lets have a look the freq of the clubs which Loaned players.
df['Loaned From'].value_counts()
# There are 341 clubs that have loaned players and Atalanta has loaned a maximum of 20 players.

# Further analysing, we see that the players which have valid data in Loaned from column have contract valid till a date in 2018 or 2019.
# This is old info, now lets think they were retained or bought by their current clubs. Hence 'Loaned From' column is not needed now.
# For these players, lets set their contracts valid till data to be 2 years from now. So, lets set it 2022.
# Also, for those players, lets set the 'Joined' date to be Jul 1, 2019. Assuming deal happened mid last year.

df=df.drop(['Loaned From'],axis=1)

df.loc[(pd.isnull(df.Joined)), 'Contract Valid Until'] = '2022'
df.Joined.fillna('Jul 1, 2019',inplace=True)

# Now, for the 'Release Clause' column, lets set their value as the mean of the values of that player's rating.
# For this, first we need to convert the data in this column to a numeric value.
# We will remove '€' symbol and tackle 'M' and "K' string with correct multiplication factors.
# So lets create a function for currency conversion.
def currency_converter(val):
    amount = val.replace('€','')
    if 'K' in amount:
        factor=pow(10,3)
        amount = float(amount.replace('K', ''))*factor
    elif 'M' in amount:
        factor=pow(10,6)
        amount = float(amount.replace('M', ''))*factor
    return float(amount)

# We will apply this function to Value, Wage and columns
df.Value =  df.Value.apply(lambda x: currency_converter(x))
df.Wage =  df.Wage.apply(lambda x: currency_converter(x))

df['Release Clause'].loc[(pd.notna(df['Release Clause']))] =  df['Release Clause'].loc[(pd.notna(df['Release Clause']))].apply(lambda x: currency_converter(x))
df['Release Clause']=df['Release Clause'].astype(float)

#df['Release Clause']=df['Release Clause'].replace('[\€]', '', regex=True)
#for i in range(len(df['Release Clause'])):
#    if pd.isnull(df['Release Clause'].iloc[i])==False:
#        release_val=df['Release Clause'][i][:-1]
#        if df['Release Clause'][i][-1]=='M':
#            factor=pow(10,6)
#        elif df['Release Clause'][i][-1]=='K':
#            factor=pow(10,3)
#        else: continue
#        df['Release Clause'][i]=pd.to_numeric(release_val)*factor
#    else: continue

df_RC_Overall=df[['Release Clause','Overall']]
df_RC_Overall_null=df_RC_Overall[df['Release Clause'].isnull()]
df_RC_Overall_notnull=df_RC_Overall.dropna(subset=['Release Clause'])
df_RC_Overall_notnull=df_RC_Overall_notnull.reset_index(drop=True)
df_means=df_RC_Overall_notnull.groupby(['Overall']).mean()
df_means=df_means.reset_index()

for i in range(len(df)):
    if pd.isnull(df['Release Clause'].iloc[i])==True:
        rating=df.Overall[i]
        df['Release Clause'][i]=df_means['Release Clause'][df_means.Overall==rating]
    else: continue

#df_RC_Overall_null.join(df_means.set_index('Overall'),on='Overall')

# Checking null values again, we see almost all the data is cleaned now
df_null_count=df.isna().sum()
df_null_count=df_null_count[df_null_count>0]
# There are 26 columns having 1992 missing values ('nan'). This is exactly the same number of goalkeepers in the dataset.
len(df_GK)
# The reason they are null is because Goalkeepers wont have these positional attributes of other players. Hence, they should logically be nan.
# While comparing the positional attributes, we should make sure, we dont compare other players with Goalkeeprs.
# Same goes by comparing attributes of Goalkeeper with other players.

# Now lets set the datatypes of columns correctly.
df.info()

# We have now logically cleaned our data. Lets see the data is not having abnormal entries.
df.nunique()
# The data shows players are from 163 different countries, 651 Clubs.
df.Age.describe() # Min age is 16 and eldest player is of age 45.
sns.countplot(df.Age)

# Define functions for different types of plots to use in future as and when needed.
'''Function to distribution plot'''
def distplot(feature, col):
    global ax
    font_size = 16
    title_size = 20
    plt.rcParams['figure.figsize'] = (12, 5)
    ax = sns.distplot(feature, color = col)
    plt.xlabel('%s' %feature.name, fontsize = font_size)
    plt.ylabel('Count of the Players', fontsize = font_size)
    plt.xticks(fontsize = font_size)
    plt.yticks(fontsize = font_size)
    plt.title('%s' %feature.name + ' Distribution of Players', fontsize = title_size)
    plt.show()

'''Function to count plot'''
def countplot(feature, title, color):
    global ax
    font_size = 14
    title_size = 20
    plt.rcParams['figure.figsize'] = (12, 5)
    ax = sns.countplot(feature, palette = color)
    plt.xlabel('%s' %feature.name, fontsize = font_size)
    plt.ylabel('Count of the Players', fontsize = font_size)
    plt.xticks(fontsize = font_size)
    plt.yticks(fontsize = font_size)
    plt.title(title, fontsize = title_size)
    plt.show()

countplot(df.Age,'Distribution of Players across Age groups','coolwarm')
distplot(df.Age,'g')
sns.set_style('whitegrid')
sns.boxplot(data=df.Age)
# We see age is as expected clustered around mid 20s and is right skewed.
# There is no outlier and abnormal value in Age column.

# Lets visualise the nationality data
df.Nationality.value_counts()
# This shows most of the players are from England. Lets visualise top 10 countries.
sns.barplot(x='index',y='Nationality',data=df.Nationality.value_counts()[:10].reset_index())
plt.xlabel('Nationality')
plt.ylabel('Count of the players')
plt.title('Players distribution among top 10 countries')

df_describe=df.describe() # analysing data across various columns by storing in dataframe
# Analysing this we see Potential and Overall are also having no abnormal data

# Analysing clubs
df.Club.value_counts()
# There are 651 clubs with number of players ranging from 33 to 19. So, data seems to be reasonable.

# Lets have a look at player's value
# df_describe shows min value is 0. Lets find out more.
df_val_0=df[df.Value==0]
# There are 11 such players, with age range of 39 to 44 with mostly 40 as the age of collection.
# Exact reason couldn't be found out just with the current data and some background check needs to be done.
# Let's not worry about these 11 player's Value now.
# Let's visualise Value distribution of players
distplot(df.Value,'g')
# We see the distribution being highly right skewed which is expected as only few players are valued very high.
# This can be seen from the means and other statistic paramters in df_describe for Value. Same goes for wage.
# The mean value is 2.44863 M dollars.
df[['Name','Value','Wage','Potential','Age','Nationality']][df.Value==max(df.Value)]
# We can see that Neymar Jr. has the highest value.
# Let's find out the top 5 valued players
df[['Name','Value','Wage','Potential','Age','Nationality']].sort_values(by=['Value'],ascending=False).head(5)
# Interesting, no Christiano Ronaldo in the list of top 5. But, all class players in the list.

# Lets do similar analysis for Wage of Players.
distplot(df.Wage,'g')
df[['Name','Value','Wage','Potential','Age','Nationality']].sort_values(by=['Wage'],ascending=False).head(5)
# We can see some shuffling in the lsit now with Messi having the highest wage.

# Let's analyse Special attribute of players
distplot(df.Special,'g')
sns.boxplot(data=df.Special)
# From the plots, we see this paramter is not having much otliers and values are distributed close to normal distribution (A bit left skewed).
# Lets find which top 10 players are most special
df[['Name','Special','Overall','Nationality']].sort_values(by=['Special'],ascending=False).head(10)
# Suarez, De Bruyne, Modric have high special attribute.

# Time to analyse the preferred foot of players.
sns.countplot(df['Preferred Foot'])
plt.title('Most Preferred Foot of the Players', fontsize = 14)
# Clearly, there are more number of Right footed players

# Analyzing International Reputation
df['International Reputation'].value_counts()
# Many players have reputaion of 1 and only 6 players are rated 5. Let's have a look at them.
df[['Name','Value','International Reputation','Overall','Age','Nationality']][df['International Reputation']==5]
# Greats of the game who are well known are the world are listed. Also, Ibrahimović makes the cut.

# Analyzing Weak Foot
sns.countplot(df['Weak Foot'])
# This is normally distributed. Majority players dont have higher ratings of their weak foot.
df['Weak Foot'].value_counts() # Also, players having very less skill with their weak foot is also rare.

# Analyzing Skill Moves
sns.countplot(df['Skill Moves'])
# Majority of players have rating of 2 and 3 for their skills.
df['Skill Moves'].value_counts() # There are 50 players with skill moves of 5. Lets see top 10 sorted by their overall rating.
df[['Name','Skill Moves','Overall','Potential','Nationality','Age']][df['Skill Moves']==5].sort_values(by=['Overall'],ascending=False).head(10)
# Interstingly Messi doesn't appear to be in the list. Need to ask FIFA to update his skill rating, lol.
# K. Mbappé is highly rated for skill moves and is only 19. Quite a potential. His potential rating is highest in the list.

# Analyzing Work Rate
sns.countplot(df['Work Rate'])
# We can see maximum number of players have medium attack/defense work rate.
df['Work Rate'].value_counts()
# Only 34 players are have low work rate in both.
df[['Name','Work Rate','Overall','Club','Age']][df['Work Rate']=='Low/ Low'].sort_values(by=['Overall'],ascending=True).head(10)
# Obviously, these players are rated low and would have to work harder to get good contracts.
sns.violinplot(x='Work Rate', y='Special', data=df)
# We can see that players with high work rate in either attack, defense or both are rated more special.

# Analyzing Body Type
df['Body Type'].value_counts()
# We can see there are three major categories of Body types - Normal, Lean, Stocky.
# Other body types are named mostly as player names. We need to update that.
body_type=['Normal','Lean','Stocky']
for i in range(len(df)):
    if df['Body Type'][i] not in body_type:
        df['Body Type'][i]='Lean'
    else: continue

countplot(df['Body Type'],"Distribution of Player's body type",'coolwarm')
# We see majority of players have Normal body type and few have stocky body type

# Analyzing Position
df.Position.value_counts()
len(df.Position.unique())
plt.rcParams['figure.figsize'] = (18, 10)
sns.countplot(df.Position, palette='bone')
# Data seems to be clean for this column.

# Analysing contract expiry years
df['Contract Valid Until'].value_counts()
# The values are listed as object. Let's convert the data type
df['Contract Valid Until']=df['Contract Valid Until'].astype(int)
# Data looks clean for this set. Lets see which players have contracts ending in 2026
df[['Name','Contract Valid Until','Overall','Club','Age']][df['Contract Valid Until']==2026]

# Analyzing height and weight of players
# Lets convert the data in the columns to cms and remove 'lbs'

'''For Height'''
def feet_to_cms(value): 
    tmp = value.split("'")
    return float(round((int(tmp[0]) * 12 + int(tmp[1]))*2.54)) #converting feet to cms

'''For weight'''
def extract_value_from(value):
    x = value.replace('lbs', '')
    return float(x)

df['Height'] = df['Height'].apply(lambda x: feet_to_cms(x))
df['Weight'] = df['Weight'].apply(lambda x: extract_value_from(x))
df=df.rename(columns={'Height': 'Height (cms)', 'Weight': 'Weight (lbs)'})
plt.figure(figsize = (20, 12))
ax = sns.countplot(x = 'Height (cms)', data = df, palette = 'dark')

plt.figure(figsize = (20, 12))
ax = sns.countplot(x = 'Weight (lbs)', data = df, palette = 'dark')

# Analyzing columns from LS to RB, Positional attributes
# The data has '+' between ratings and additional potential and current growth
# Let's add them and have a single value in those field and convert the data type.
# nans are seen only for GKs.

pos_cols=list(df.loc[:,'LS':'RB'].columns)

def pos_convert(val): # converting positional attributes
    tmp = val.split("+")
    return (int(tmp[0]) + int(tmp[1]))

for i in pos_cols:
    df[i].loc[(pd.notna(df.LS))] = df[i].loc[(pd.notna(df.LS))].apply(lambda x: pos_convert(x))

df.loc[:,'LS':'RB']=(df.loc[:,'LS':'RB'].loc[(pd.notna(df.LS))]).astype(int)

#Let's create a list of top 10 nationalities
top_countries=df.Nationality.value_counts().head(10).index.to_list()

# Now all the data is clean and ready for bivariate analysis.
sns.violinplot(y = df.Age, x = df['Preferred Foot'], palette = 'Reds') # No correlation between them
sns.lmplot(x='Age',y='Overall',data=df)
sns.lineplot(df['Age'], df['Overall'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Value'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Release Clause'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Potential'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Wage'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Stamina'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Penalties'], palette = 'Wistia')
sns.lineplot(df['Age'], df['Contract Valid Until'], palette = 'Wistia')

sns.violinplot(y='Weight (lbs)',x='Work Rate',hue='Preferred Foot',data=df)
plt.figure(figsize = (20, 12))