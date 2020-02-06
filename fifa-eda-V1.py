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

for i in range(len(df)):
#    a=pd.isnull(df['Joined'].iloc[i])
    if pd.isnull(df['Joined'])[i]==True:
        df['Joined'].iloc[i]='Jul 1, 2019'
        df['Contract Valid Until'].iloc[i]='2022'
    else: continue

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
#df['Release Clause'] =  df['Release Clause'].apply(lambda x: currency_converter(x))

df['Release Clause']=df['Release Clause'].replace('[\€]', '', regex=True)
for i in range(len(df['Release Clause'])):
    if pd.isnull(df['Release Clause'].iloc[i])==False:
        release_val=df['Release Clause'][i][:-1]
        if df['Release Clause'][i][-1]=='M':
            factor=pow(10,6)
        elif df['Release Clause'][i][-1]=='K':
            factor=pow(10,3)
        else: continue
        df['Release Clause'][i]=pd.to_numeric(release_val)*factor
    else: continue
    
df['Release Clause']=df['Release Clause'].astype(float)
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
    plt.rcParams['figure.figsize'] = (12, 4)
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
    plt.rcParams['figure.figsize'] = (12, 6)
    ax = sns.countplot(feature, palette = color)
    plt.xlabel('%s' %feature.name, fontsize = font_size)
    plt.ylabel('Count of the Players', fontsize = font_size)
    plt.xticks(fontsize = font_size)
    plt.yticks(fontsize = font_size)
    plt.title(title, fontsize = title_size)
    plt.show()
    
'''Function to pie chart''' 
def piechart(variable, title, color):
    labels = ['1', '2', '3', '4', '5']
    variable = variable.value_counts()
    explode = [0.1, 0.1, 0.2, 0.5, 0.9]
    plt.rcParams['figure.figsize'] = (9, 9)
    plt.pie(variable, labels = labels, colors = color, explode = explode, shadow = True)
    plt.title(title, fontsize = 20)
    plt.legend()
    plt.show()

countplot(df.Age,'Distribution of Players across Age groups','coolwarm')
distplot(df.Age,'g')
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