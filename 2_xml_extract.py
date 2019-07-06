# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 14:31:40 2019

@author: 1
"""
from functools import partial
from urllib.request import urlopen,Request
from urllib.error import URLError
import pymongo
import multiprocessing
'''
Acquire the xml files of citations from PLOS ONE, meanwhile record the error in "error.log"
'''
def PLOS_get(path,i,cursor):
    for docu in cursor:
        link = docu["doi_link"]
        cited_no = docu["cited_no"]
        try:
            url = "http://journals.plos.org/plosone/article/file?id="+link+"&type=manuscript"
            i=i+1
            req = Request(url)
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
            html = urlopen(req)
            name = path + "\\" + str(i) + ".xml"
            collection.update_one({'doi_link': link,'cited_no':cited_no},{'$set':{'content_path':name}})
            with open(name, 'wb') as f:
                f.write(html.read())
                print(link,"               ",name)
#                time.sleep(1)
        except URLError as e:
            with open(path + "\\error.log",'a') as f:
                f.write(str(i)+"    "+str(link)+"    "+str(e.code)+'\n')
            pass

'''
According to "error.log", revise the DOI manually and  get the rest of xml files of citations from PLOS ONE
'''      
def PLOS_revise(t_links,path,collection):
    f_links = []
    f_nos = []
    with open(path + "//error.log",'r') as f:
        f = f.readlines()
        for line in f:
            f_nos.append(line.split("    ")[0])
            f_links.append(line.split("    ")[1])
    for i in range(len(t_links)):
        url = "http://journals.plos.org/plosone/article/file?id="+t_links[i]+"&type=manuscript"
        req = Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
        html = urlopen(req)
        name = path + "\\" + str(f_nos[i]) + ".xml"
        collection.update_many({'doi_link': f_links[i]},{'$set':{'doi_link': t_links[i],'content_path':name}})
        with open(name, 'wb') as f:
            f.write(html.read())
            print(t_links[i],"               ",name)
            
client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations']

cursor = collection.find({'cited_no': {'$lte': 10}})
path = "Citation_paper\\1"
PLOS_get(path,0,cursor)

#path = "Citation_paper\\1"
#pool = multiprocessing.Pool()
#func = partial(PLOS_get,path,0)
#pool.map(func, cursor)
#pool.close()
#pool.join()

t_links = ["10.1371/journal.pone.0186943","10.1371/journal.pone.0176993","10.1371/journal.pone.0197599","10.1371/journal.pone.0186461"]
PLOS_revise(t_links,path,collection)

cursor = collection.find({'cited_no': {'$gt': 10}})
path = "Citation_paper\\2"
PLOS_get(path,0,cursor)

t_links = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0180444"]
PLOS_revise(t_links,path,collection)