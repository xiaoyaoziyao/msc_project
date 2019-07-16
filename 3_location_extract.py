# -*- coding: utf-8 -*-
"""
Extract the location
"""
import nltk
from nltk.corpus import stopwords
import pymongo
import re
import distance

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

stand_title = ["Others","Introduction and Background",
               "Materials and Methods","Results and Discussion","Conclusion"]
'''
Extract the rid and location of citations from xml files
'''   
def xml_find_loc(collection,i):
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10 ,'$lte': i*10}})
    for docu in cursor:
        titles = {}
        rid_real = ''
        location = []
        target_title = docu["cited_title"]
        path = docu["content_path"]      
        try: 
            tree = ET.ElementTree(file=path)
            body = tree.getroot().find('.//body')
            year = tree.find(".//pub-date/year").text
            collection.update_one({'content_path': path,"cited_title":target_title },{'$set':{'pub_year':int(year)}})
            for elm in tree.iterfind('.//ref'):      
                if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                    f_title = elm.find(".//article-title").text.lower()
                    titles[f_title] = elm.attrib['id']
            rid_real = edit_distance(target_title,titles)
            collection.update_one({'cited_title':target_title,'content_path': path},{'$set':{'reference_id':rid_real}})
#            print("updata path:",path,",updata rid:",rid_real)
            for sec in body:
                for xref in sec.iterfind('.//xref'):
                    if(xref != None and xref.attrib["rid"] == rid_real):
                        location.append(sec[0].text)
            if(len(rid_real) != 0 and len(location) == 0):
                xml_find_revise(tree,body,rid_real,location)
#                print("updata path:",path,",updata rid:",rid_real,"cited_location",list(set(location)))
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

'''
Preprocess the standard titles and locations to help do the comparison
'''
def preprocess(sentence):
    tokens = [i.lower() for i in nltk.word_tokenize(sentence)]
    filtered = [word for word in tokens if word not in stopwords.words('english')]
    s = nltk.stem.SnowballStemmer('english')
    tokens = [s.stem(i) for i in filtered if i.isalpha()]
    return tokens

def compare(location):
    loc_num = 0
    loc = "Others"
    loc_tokens = preprocess(location)
    stand_pre = [preprocess(title) for title in stand_title]
    for l in loc_tokens:    
        for i in range(len(stand_pre)):
            if l in stand_pre[i]:
                loc = stand_title[i]
                loc_num = i
                break
#    print(loc,loc_num)
    return(loc,loc_num)
                
'''
Standardize the citation locations to help do the visualization
'''   
def standard_loc(collection,i):    
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10 ,'$lte': i*10},"cited_location" : {'$exists': True }})    
    for docu in cursor:
        try:
            stand_loc = []
            stand_num = []
            path = docu["content_path"]
            location = docu["cited_location"]
            if (len(location) != 0):
                for loc in location:
                    stand = compare(loc)
                    stand_loc.append(stand[0])
                    stand_num.append(stand[1])
                collection.update_one({'content_path': path,"cited_location":location},{'$set':{'stand_location':stand_loc,'location_num':stand_num}})
        except Exception as e:
            pass
            print(path,'Reason:', str(e), '\n')
            
def main_function(i):           
    client = pymongo.MongoClient('localhost:27017',connect = True)
    db = client['msc_project']
    collection = db['citations']        
    xml_find_loc(collection,i)
    standard_loc(collection,i)
    client.close() 

#main_function(6)
#main_function(7)

    
client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations']
print(collection.find({"cited_no":{"$gt":20},"location_num":{"$exists":False}}).count())