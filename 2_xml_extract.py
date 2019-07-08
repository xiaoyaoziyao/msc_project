# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 14:31:40 2019

@author: 1
"""
from functools import partial
import multiprocessing

from urllib.request import urlopen,Request
from urllib.error import URLError
import pymongo
import os

'''
Acquire the xml files of citations from PLOS ONE, meanwhile record the error in "error.log"
'''
def PLOS_get(path,collection,i):
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10 ,'$lte': i*10}})
    j = 0
    if not os.path.exists(path):
        os.mkdir(path)
    for docu in cursor:
        link = docu["doi_link"]
        cited_no = docu["cited_no"]
        try:
            url = "http://journals.plos.org/plosone/article/file?id="+link+"&type=manuscript"
            j = j + 1
            req = Request(url)
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
            html = urlopen(req)
            name = path + "\\" + str(j) + ".xml"
            collection.update_one({'doi_link': link,'cited_no':cited_no},{'$set':{'content_path':name}})
            with open(name, 'wb') as f:
                f.write(html.read())
                print(link,"               ",name)
#                time.sleep(1)
        except URLError as e:
            with open(path + "\\error.log",'a') as f:
                f.write(str(j)+"    "+str(link)+"    "+str(e.code)+'\n')
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

def main_function(i):            
    client = pymongo.MongoClient('localhost:27017',connect = True)
    db = client['msc_project']
    collection = db['citations']
    
    path = "Citation_paper\\"+str(i)
    PLOS_get(path,collection,i)

def main_revise(i,t_links):
    client = pymongo.MongoClient('localhost:27017',connect = True)
    db = client['msc_project']
    collection = db['citations']
    
    path = "Citation_paper\\"+str(i)
    PLOS_revise(t_links,path,collection)
    
#pool = multiprocessing.Pool()
#func = partial(PLOS_get,path,0)
#pool.map(func, cursor)
#pool.close()
#pool.join()

#main_function(6)
#main_function(7)        

    
#t_links1 = ["10.1371/journal.pone.0186943","10.1371/journal.pone.0176993","10.1371/journal.pone.0197599","10.1371/journal.pone.0186461"]
#t_links2 = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0180444"]
#t_links3 = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0180444","10.1371/journal.pone.0188859"]
#t_links4 = ["10.1371/journal.pone.0191207","10.1371/journal.pone.0162564"]
#t_links5 = ["10.1371/journal.pone.0187044"]
#t_links6 = ["10.1371/journal.pone.0187044"]
#t_links7 = ["10.1371/journal.pone.0177179"]

