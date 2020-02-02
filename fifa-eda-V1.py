from zipfile import ZipFile
import os
import pandas as pd

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

# Goal keeps dont have attributes such as LS, ST, RS, etc attribute. Hence they all have null values in them.
# So lets create another dataframe for position='GK'.
# In future analysis when all players are analyses together, we dont considered such columns.
df_GK=df[df['Position']=='GK']
#for i in df_null_cols:
#    df_name='df_'+df_null_cols[i]+'_null'