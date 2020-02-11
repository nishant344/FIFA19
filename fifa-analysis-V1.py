from sklearn.externals import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # matplotlib for plotting
import seaborn as sns # seaborn for better graphics

df = joblib.load("fifa19_df_clean.pkl")

#Let's create a list of top 10 nationalities
top_countries=df.Nationality.value_counts().head(10).index.to_list()

# Lets create functions of plots for bivariate analysis
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