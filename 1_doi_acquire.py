"""
Archive the xml files
"""
import re
import os
import pymongo

'''
Extract the DOI of citations
'''
def file_list(path):
    files = []
    for file in os.listdir(path):
        files.append(path+"\\"+file)
    return files

def DOI_find(collection,file,num):
    doi_dic = {}
    f = open(file,'r', encoding='UTF-8')
    for line in f:
        g = re.search("(?<=DI )10\.([0-9]{4}).*", line)                
        if g:
            doi_dic = {"cited_no":int(re.findall('\((.*?)\)', file)[0]) + num,"doi_link":str(g.group())}
            if not collection.find_one(doi_dic):
                collection.insert_one(doi_dic)
    f.close()  
'''
Extract the titles of highly-cited papers
'''
def DOI_find_highpaper(collection,file,num):
    with open(file,'r', encoding='UTF-8') as f:
        f = f.readlines()
        i = 0
        for line in f:
            y = re.search("(?<=PY ).*$", line)
            t = re.search("(?<=TI ).*$", line)
            if t:
                if(f[i+1].startswith('SO')):
                    title = t.group()
                else:
                    title = t.group() + f[i+1].replace('\n','') .replace('  ','') 
                num = num + 1
                collection.update_many({'cited_no': num},{'$set':{'cited_title':title}})
            if y:
                year = y.group()                
                collection.update_many({'cited_no': num},{'$set':{'cited_year':int(year)}})
            i = i + 1                      

'''
Main function
'''
client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations']

files = file_list("WOS_list\\1")
num = 0
for file in files:
    if "(" in file and ")" in file:
        DOI_find(collection,file,num)
    else:
        DOI_find_highpaper(collection,file,num)

files = file_list("WOS_list\\2")
num = 10
for file in files:
    if "(" in file and ")" in file:
        DOI_find(collection,file,num)
    else:
        DOI_find_highpaper(collection,file,num)
client.close()    







