# -*- coding: utf-8 -*-
"""
Visualize the data
"""
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sns
import pymongo

client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations']

cursor = collection.find({'$and':[{"cited_no":{'$lte':10}},
                                 {"location_num":{'$exists':True}}]})
cited_nos = []
year_diffs = []
locations = []
cited_years= []
for docu in cursor:
    year_diff = docu["citation_year"] - docu["cited_year"]
    cited_no = docu["cited_no"]
    location = docu["stand_location"]
    cited_year = docu["cited_year"]
    for i in range(len(location)):
        year_diffs.append(year_diff)
        cited_nos.append(cited_no)
        cited_years.append(cited_year)
    for loc in location:
        locations.append(loc)
no_year = list(zip(cited_nos,cited_years))
data = {'cited_no_year':no_year,'year_diff':year_diffs,'location':locations}
df = pd.DataFrame(data=data)
plt.figure(figsize=(24,12),dpi=80)
# sns.violinplot(x='cited_no_year',y='year_diff',hue='location',inner='stick',data=df)
sns.swarmplot(x='cited_no_year',y='year_diff',hue='location', data=df)
plt.show()
plt.savefig('result.png')

client.close()  