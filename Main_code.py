import re
import os
import time
from urllib.request import urlopen,Request
from urllib.error import URLError
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import distance
from collections import Counter
import matplotlib.pyplot as plt 
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC 
from sklearn.cross_validation import cross_val_score
from sklearn.learning_curve import learning_curve
import pymongo
import time

stand_title = {0:"Others",
               1:"Introduction",
               2:"Literature Review \ Related work",
               3:"Methods \ Methodology",
               4:"Results",
               5:"Discussion",
               6:"Conclusion"}
'''
Extract the DOI of citations
'''
def file_list(path):
    files = []
    for file in os.listdir(path):
        files.append(path+"//"+file)
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
                collection.update_many({'cited_no': num},{'$set':{'cited_year':year}})
            i = i + 1                      

'''
Acquire the xml files of citations from PLOS ONE, meanwhile record the error in "error.log"
'''
def PLOS_get(collection,path,num):
    i = 0
    cursor = collection.find({'cited_no': {'$gt': num}})
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
            collection.update_many({'doi_link': link,'cited_no':cited_no},{'$set':{'content_path':name}})
            with open(name, 'wb') as f:
                f.write(html.read())
                print(link,"               ",name)
                time.sleep(1)
        except URLError as e:
            with open(path + "//error.log",'a') as f:
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
            time.sleep(1)


'''
Extract the rid and location of citations from xml files
'''   
def xml_find_loc(collection,num):
    titles = {}
    rid_real = ''
    cursor = collection.find({'cited_no': {'$gt': num}})
    for docu in cursor:
        location = []
        target_title = docu["cited_title"]
        path = docu["content_path"]      
        try: 
            tree = ET.ElementTree(file=path)
            body = tree.getroot().find('.//body')
            year = tree.find(".//pub-date/year").text
            collection.update_one({'content_path': path,"cited_title":target_title },{'$set':{'pub_year':year}})
            for elm in tree.iterfind('.//ref'):      
                if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                    f_title = elm.find(".//article-title").text.lower()
                    titles[f_title] = elm.attrib['id']
            rid_real = edit_distance(target_title,titles)
            collection.update_one({'cited_title':target_title,'content_path': path},{'$set':{'reference_id':rid_real}})
            print("updata path:",path,",updata rid:",rid_real)
            for sec in body:
                for xref in sec.iterfind('.//xref'):
                    if(xref != None and xref.attrib["rid"] == rid_real):
                        location.append(sec[0].text)
            if(len(location) == 0):
                xml_find_revise(tree,body,rid_real,location)
            collection.update_one({'content_path': path},{'$set':{'cited_location':list(set(location))}})
        except Exception as e:
            pass
            print(path,'Reason:', str(e), '\n')

def xml_find_revise(tree,body,rid_real,location):
    for elm in tree.iterfind('.//ref'):
        if elm.attrib['id'] == rid_real:
            label = elm.find(".//label").text
    for sec in body:
        for xref in sec.iterfind('.//xref'):
            if(xref.tail == '–' and not re.search('[a-zA-Z]', xref.text)):
                xref_text = ''.join(c for c in xref.text if c.isdigit())
                if(abs(int(xref_text)-int(label)) < 4 and int(xref_text) < int(label)):
                    location.append(sec[0].text)
'''
Calculate the levenshtein distance to do fuzzy match for titles
'''   
def edit_distance(target,titles):
    rid_real = ''
    dis = []
#    diff = []
    for title in titles.items():       
        dis.append(distance.levenshtein(target, title[0]))
    dis_index = dis.index(min(dis))
#    real_title = list(titles)[dis_index]
    rid_real = list(titles.values())[dis_index]
#    if(min(dis) >= 20 and abs(len(target) - len(real_title)) >= 20):
#        for title in titles.items():    
#            seq = difflib.SequenceMatcher(None,target, title[0])
#            diff.append(seq.ratio())
#        diff_index = diff.index(max(diff))
#        real_title = list(titles)[diff_index]
#        rid_real = list(titles.values())[diff_index]
#    print(target)
#    print(real_title)
#    print(file)
    return rid_real


def preprocess(sentence):
    tokens = [i.lower() for i in nltk.word_tokenize(sentence)]
    s = nltk.stem.SnowballStemmer('english')
    tokens = [s.stem(i) for i in tokens if i.isalpha()]
    return tokens

'''
Read the results.txt as lists and save them into csv files to help visualize the data
   
def read_results():
    a = []
    b = []
    c = []
    d = []
    n = []
    global stand_title
    for key,value in stand_title.items():
            stand_title[key]=preprocess(value)
    for k in range(1,12):
        savefile = "Results\\2\\result(" + str(k) +").txt"
        with open(savefile,'r') as f:
            lines = f.readlines()
            year = lines[1][13:].replace('\n','')
            for i in range(3,len(lines)-2):
                if(lines[i].startswith('Location:') and lines[i+1].startswith('Year_Diff:')):
                    loc = lines[i][10:].replace('\n','')
                    loc = preprocess(loc)
                    loc = standard_loc(loc)
                    a.append(loc)
                    y_diff = int(lines[i+1][11:].replace('\n',''))
                    b.append(y_diff)
                    n.append(k)
                    d.append(year)
        c.append(year)
    dataframe = pd.DataFrame({'file':n,'location':a,'year_diff':b,'year_pub':d})
    dataframe.to_csv("data2.csv",index=False,sep=',')
    return c
'''

def standard_loc(loc): 
    for i in loc:
        for key,value in stand_title.items():
            if i in value:
                loc = key
                break
    if loc not in range(1,7):
         loc = 0
    return loc    

'''
Main function
'''
#start = time.clock()
client = pymongo.MongoClient('localhost:27017',connect =True)
db = client['msc_project']
collection = db['citations']
#files = file_list("WOS_list\\1")
num = 0
#for file in files:
#    if "(" in file and ")" in file:
#        DOI_find(collection,file,num)
#    else:
#        DOI_find_highpaper(collection,file,num)
#elapsed = (time.clock() - start)
#print("Time used1:",elapsed)
#path = "Citation_paper\\1"
#PLOS_get(collection,path,num)
#elapsed = (time.clock() - start)
#print("Time used2:",elapsed)
#t_links = ["10.1371/journal.pone.0186943","10.1371/journal.pone.0176993","10.1371/journal.pone.0197599","10.1371/journal.pone.0186461"]
#PLOS_revise(t_links,path,collection)
#elapsed = (time.clock() - start)
#print("Time used3:",elapsed)
xml_find_loc(collection,num)

#files = file_list("WOS_list\\2")
#num = 10
#for file in files:
#    if "(" in file and ")" in file:
#        DOI_find(collection,file,num)
#    else:
#        DOI_find_highpaper(collection,file,num)
#path = "Citation_paper\\2"
#PLOS_get(collection,path,num)
#t_links = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0063671"]
#PLOS_revise(t_links,path,collection)
#xml_find_loc(collection,num)
#client.close()    

###Finished part###

##citations of top 10 highly-cited paper


    
#
##manually revision according to "error.log"
#PLOS_revise("10.1371/journal.pone.0186943",1,113)
#PLOS_revise("10.1371/journal.pone.0176993",1,149)
#PLOS_revise("10.1371/journal.pone.0197599",2,6)
#PLOS_revise("10.1371/journal.pone.0186461",9,12)
#PLOS_revise("10.1371/journal.pone.0063671",3,62)
#PLOS_revise("10.1371/journal.pone.0180444",8,13)
#
##Extract year and location of citations
#targets_title = DOI_find_highpaper()[0]
#targets_year = DOI_find_highpaper()[1]
#for i in range(1,12):
#    print("Highly-cited paper " + str(i) + "......")
#    xml_find_loc(i,targets_title[i-1],targets_year[i-1]) 

###Ongoing part###

#c = read_results()
#data1 = pd.read_csv('data1.csv')
#data2 = pd.read_csv('data2.csv')
#frames = [data1,data2]
#data = pd.concat(frames,axis=0,keys=['data1','data2'], join='outer')

#fig,axes=plt.subplots(1,1,figsize=(10,4),dpi=80) 
#violin plot
#sns.violinplot(x=data["year_diff"]+data["year_pub"],y="year_pub",hue='location',inner='stick',data=data1)
##scatter plot
#sns.swarmplot(x="year_pub",y="year_diff",hue='location', data=data)
#plt.savefig('result.png')

#for i in range(1,11):
#    fig,axes=plt.subplots(1,1,figsize=(10,4),dpi=80) 
#    sns.violinplot(x="year_diff",y="location",data=data[data['file']==i])
#    plt.legend([c[i-1]])

#X = list(zip(data['year_pub'],data['year_diff']))
#y = data['location']
#
#train_sizes, train_loss, test_loss = learning_curve(
#    SVC(gamma=0.001), X, y, cv=10, scoring='neg_mean_squared_error',
#    train_sizes=[0.25, 0.5, 0.75, 1])
#train_loss_mean = -np.mean(train_loss, axis=1)
#test_loss_mean = -np.mean(test_loss, axis=1)
#plt.plot(train_sizes, train_loss_mean, 'o-', color="r",
#         label="Training")
#plt.plot(train_sizes, test_loss_mean, 'o-', color="g",
#        label="Cross-validation")
#plt.xlabel("Training examples")
#plt.ylabel("Loss")
#plt.legend(loc="best")
#plt.show()
#
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
#model = SVC()
#score = cross_val_score(model,X,y,scoring='accuracy')
#model.fit(X_train,y_train)
#print(score.mean())



