import pandas as pd 
import urllib
import bs4


# contains 72 lists 

# source url 
source = 'https://www.cs.columbia.edu/~hgs/audio/harvard.html'

# save the source as html file using urllib
urllib.request.urlretrieve(source, 'voiceCloning/sentances/harvard.html')

# load the harvard.html file as harvard
harvard = open('voiceCloning/sentances/harvard.html', 'r')

# using bs4 load the source
soup = bs4.BeautifulSoup(harvard)

# loop through each <ol> tag and extract each sentance from the list as a dictionary
# and append it to the list
sentances = []
for ol in soup.find_all('ol'):
    for li in ol.find_all('li'):
        sentances.append({'sentance': li.text})

# convert the list to a pandas dataframe
df = pd.DataFrame(sentances)

# create a new column called list and group each row by 10 and assign a number to it
df['list'] = df.index // 10
df['list'] = df['list'] + 1

# create a new ID variable called senId and assign sen_ to each row starting at 1
df['senId'] = 'sn_' + (df.index + 1).astype(str)

# remove all special characters from the sentance column
df['sentance'] = df['sentance'].str.replace('[^\w\s]','')

# save the dataframe as sentances.csv
df.to_csv('voiceCloning/sentances/sentances.csv', index=False)

