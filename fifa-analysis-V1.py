from sklearn.externals import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # matplotlib for plotting
import seaborn as sns # seaborn for better graphics

df = joblib.load("fifa19_df_clean.pkl")

#Let's create a list of top 10 nationalities
top_countries=df.Nationality.value_counts().head(10).index.to_list()

# Lets create functions of plots for bivariate analysis. X-axis - discrete variables, Y-axis - continuous variables
def violinplot(disc_var,cont_var,fig_size_tup=(12,5),palette='Set3',data=df,hue=None):
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    font_size = 16
    title_size = 20
    plt.figure(figsize = fig_size_tup)
    sns.violinplot(x=disc_var,y=cont_var,hue=hue,data=data,palette=palette)
    plt.xlabel('%s' %disc_var, fontsize = font_size)
    plt.ylabel('%s' %cont_var, fontsize = font_size)
    plt.xticks(fontsize = font_size)
    plt.yticks(fontsize = font_size)
    plt.title('%s' %cont_var + ' v/s %s' %disc_var, fontsize = title_size)
    plt.show()

violinplot('International Reputation','Age',hue='Preferred Foot')

# list of continuous and discrete variables of interest
cont_var=['Age','Overall','Potential','Value','Wage','Special','Height (cms)','Weight (lbs)','Release Clause']
disc_var=['Preferred Foot','International Reputation','Weak Foot','Skill Moves','Work Rate','Body Type','Position','Contract Valid Until']

for x, y in [(x,y) for x in disc_var for y in cont_var]:
    violinplot(x,y,fig_size_tup=(14,7))

sns.pairplot(vars=['Age','Overall','Value','Special','Height (cms)','Weight (lbs)','Release Clause'],data=df)

g = sns.PairGrid(df,y_vars=cont_var,x_vars=disc_var,height=4)
g.map(sns.lineplot)
g.add_legend();


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

# plotting a pie chart to represent share of international repuatation
labels = ['1', '2', '3', '4', '5']
sizes = df['International Reputation'].value_counts()
colors = plt.cm.copper(np.linspace(0, 1, 5))
explode = [0.1, 0.1, 0.2, 0.3, 0.4]

plt.rcParams['figure.figsize'] = (12, 12)
plt.pie(sizes, labels = labels, colors = colors, explode = explode, shadow = True)
plt.title('International Repuatation for the Football Players', fontsize = 20)
plt.legend()
plt.show()

# plotting a pie chart to represent the share of week foot players
labels = ['5', '4', '3', '2', '1'] 
size = df['Weak Foot'].value_counts()
colors = plt.cm.Wistia(np.linspace(0, 1, 5))
explode = [0, 0, 0, 0, 0.1]
plt.pie(size, labels = labels, colors = colors, explode = explode, shadow = True, startangle = 90)
plt.title('Distribution of Week Foot among Players', fontsize = 25)
plt.legend()
plt.show()

# Adding new parameters/features based on combination of existing skill sets.
def defending(df):
    return int(round((df[['Marking', 'StandingTackle', 'SlidingTackle']].mean()).mean()))

def general(df):
    return int(round((df[['HeadingAccuracy', 'Dribbling', 'Curve', 'BallControl', 'Stamina']].mean()).mean()))

def mental(df):
    return int(round((df[['Aggression', 'Interceptions', 'Positioning', 'Vision','Composure']].mean()).mean()))

def passing(df):
    return int(round((df[['Crossing', 'ShortPassing', 'LongPassing']].mean()).mean()))

def mobility(df):
    return int(round((df[['Acceleration', 'SprintSpeed', 'Agility','Reactions']].mean()).mean()))

def power(df):
    return int(round((df[['Balance', 'Jumping', 'Stamina', 'Strength']].mean()).mean()))

def rating(df):
    return int(round((df[['Potential', 'Overall']].mean()).mean()))

def shooting(df):
    return int(round((df[['Finishing', 'Volleys', 'FKAccuracy', 'ShotPower','LongShots', 'Penalties']].mean()).mean()))

df['Defending'] = df.apply(defending, axis = 1)
df['General'] = df.apply(general, axis = 1)
df['Mental'] = df.apply(mental, axis = 1)
df['Passing'] = df.apply(passing, axis = 1)
df['Mobility'] = df.apply(mobility, axis = 1)
df['Power'] = df.apply(power, axis = 1)
df['Rating'] = df.apply(rating, axis = 1)
df['Shooting'] = df.apply(shooting, axis = 1)

# best players per each position with their age, club, and nationality based on their overall scores
df.iloc[df.groupby(df['Position'])['Overall'].idxmax()][['Position', 'Name', 'Age', 'Club', 'Nationality']]

# Every Nations' Player and their Weights
df_countries = df.loc[df['Nationality'].isin(top_countries) & df['Weight (lbs)']]

plt.rcParams['figure.figsize'] = (15, 7)
ax = sns.violinplot(x = df_countries['Nationality'], y = df_countries['Weight (lbs)'], palette = 'Reds')
ax.set_xlabel(xlabel = 'Countries', fontsize = 9)
ax.set_ylabel(ylabel = 'Weight in lbs', fontsize = 9)
ax.set_title(label = 'Distribution of Weight of players from different countries', fontsize = 20)
plt.show()

# Every Nations' Player and their overall scores
df_countries = df.loc[df['Nationality'].isin(top_countries) & df['Overall']]

plt.rcParams['figure.figsize'] = (15, 7)
ax = sns.barplot(x = df_countries['Nationality'], y = df_countries['Overall'], palette = 'spring')
ax.set_xlabel(xlabel = 'Countries', fontsize = 9)
ax.set_ylabel(ylabel = 'Overall Scores', fontsize = 9)
ax.set_title(label = 'Distribution of overall scores of players from different countries', fontsize = 20)
plt.show()

# Every Nations' Player and their wages
df_countries = df.loc[df['Nationality'].isin(top_countries) & df['Wage']]

plt.rcParams['figure.figsize'] = (15, 7)
ax = sns.barplot(x = df_countries['Nationality'], y = df_countries['Wage'], palette = 'Purples')
ax.set_xlabel(xlabel = 'Countries', fontsize = 9)
ax.set_ylabel(ylabel = 'Wage', fontsize = 9)
ax.set_title(label = 'Distribution of Wages of players from different countries', fontsize = 15)
plt.show()

# Every Nations' Player and their International Reputation
df_countries = df.loc[df['Nationality'].isin(top_countries) & df['International Reputation']]

plt.rcParams['figure.figsize'] = (15, 7)
ax = sns.boxenplot(x = df_countries['Nationality'], y = df_countries['International Reputation'], palette = 'autumn')
ax.set_xlabel(xlabel = 'Countries', fontsize = 9)
ax.set_ylabel(ylabel = 'Distribution of reputation', fontsize = 9)
ax.set_title(label = 'Distribution of International Repuatation of players from different countries', fontsize = 15)
plt.show()
