"""
Acquire DOIs of citation papers
"""
import re
import os
import pymongo


def file_list(path):
    """
    Get the list of file names in one folder
    """
    files = []
    for file in os.listdir(path):
        files.append(path+"\\"+file)
    return files


def doi_find(collection,file,num):
    """
    Extract the DOI of citations with the information file downloaded in WoS
    """
    f = open(file,'r', encoding='UTF-8')
    for line in f:
        g = re.search("(?<=DI )10\.([0-9]{4}).*", line)
        if g:
            doi_dic = {"cited_no": int(re.findall('\((.*?)\)', file)[0]) + num, "doi_link": str(g.group())}
            if not collection.find_one(doi_dic):
                collection.insert_one(doi_dic)
    f.close()


def doi_find_highpaper(collection,file,num):
    """
    Extract the titles of highly-cited papers with the information file downloaded in WoS
    """
    with open(file, 'r', encoding='UTF-8') as f:
        f = f.readlines()
        i = 0
        for line in f:
            y = re.search("(?<=^PY ).*$", line)
            t = re.search("(?<=^TI ).*$", line)
            if t:
                if(f[i+1].startswith('SO')):
                    title = t.group()
                else:
                    title = t.group() + f[i+1].replace('\n', '') .replace('  ', '')
                num = num + 1
                collection.update_many({'cited_no': num}, {'$set': {'cited_title': title}})
            if y:
                year = y.group()                
                collection.update_many({'cited_no': num}, {'$set': {'cited_year': int(year)}})
            i = i + 1                      


def main_function(i):
    """
    Main function
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']    
    files = file_list("WOS_list\\"+str(i))
    num = (i-1)*10
    for file in files:
        if "(" in file and ")" in file:
            doi_find(collection, file, num)
        else:
            doi_find_highpaper(collection, file, num)
    client.close()


'''
Several Iterations for Main function
'''
for i in range(1,12):
    main_function(i)



