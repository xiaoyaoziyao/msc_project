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
#{"cited_year":{'$gte':2006}},
#print(cursor.count())
cited_years = []
cited_nos = []
pub_years = []
locations = []
for docu in cursor:
    cited_year = docu["cited_year"]
    cited_no = docu["cited_no"]
    pub_year = docu["pub_year"]
    location = docu["location_num"]
    for i in range(len(location)):
        cited_years.append(cited_year)
        pub_years.append(pub_year)
        cited_nos.append(cited_no)
    for loc in location:
        locations.append(loc)
data = {'cited_no':cited_nos,'pub_year':pub_years,'location':locations}
df = pd.DataFrame(data=data)
#print(df)
fig,axes=plt.subplots(1,1,figsize=(20,8),dpi=80) 
#sns.violinplot(x='cited_year',y='pub_year',hue='location',inner='stick',data=df)
#
sns.swarmplot(x='cited_no',y='pub_year',hue='location', data=df)
plt.savefig('result.png')
#
#for i in range(1,11):
#    fig,axes=plt.subplots(1,1,figsize=(10,4),dpi=80) 
#    sns.violinplot(x="year_diff",y="location",data=data[data['file']==i])
#    plt.legend([c[i-1]])
#
#
#
#client.close()  