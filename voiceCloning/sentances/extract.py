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

# create a new column that counts to 10 then resets to 1
df['userFieldName'] = 'q' + (df.index % 10 + 1).astype(str)
df['id'] = 'list' + (df['list']).astype(str) + '-' + 'q' + (df.index % 10 + 1).astype(str)


# save the dataframe as sentances.csv
df.to_csv('voiceCloning/sentances/sentances.csv', index=False)






### load in phrasedata.csv.txt using pandas, splitting columns based on | and assign the columns names transcript and transcript_clean
list2 = pd.read_csv('voiceCloning/sentances/phrasedata.csv.txt', sep='|', names = ['transcript', 'sentance'])
list2 = list2.drop(['transcript'], axis=1)
# create a new column called list and group each row by 10 and assign a number to it
list2['list'] = list2.index // 10
list2['list'] = list2['list'] + 200
# create a new ID variable called senId and assign sen_ to each row starting at 1
list2['senId'] = 'sn_' + (list2.index + 1).astype(str)
# remove all special characters from the sentance column
# list2['transcript_clean'] = list2['transcript_clean'].str.replace('[^\w\s]','')
# create a new column that counts to 10 then resets to 1
list2['userFieldName'] = 'q' + (list2.index % 10 + 1).astype(str)
list2['id'] = 'list' + (list2['list']).astype(str) + '-' + 'q' + (list2.index % 10 + 1).astype(str)

# save the dataframe as sentances.csv
list2.to_csv('voiceCloning/sentances/sentances2.csv', index=False)


### merge together the two dataframes
df = pd.concat([df, list2], ignore_index=True)
### save the dataframe as sentances.csv
df.to_csv('voiceCloning/sentances/sentances3.csv', index=False)