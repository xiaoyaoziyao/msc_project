'''
extract DOI from Web of Science file
'''

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

def DOI_find(a):
    l = []
    file_object = open('WOS_list\\savedrecs ('+str(a)+').ciw','rU', encoding='UTF-8')
#    file_object = open('WOS_list\\savedrecs.ciw','rU', encoding='UTF-8')
#        name = 'out('+str(a)+').txt'
#        f = open(name,'w', encoding='UTF-8')
    i=0
    try:
        for line in file_object:
            g = re.search("(?<=DI )10\.([0-9]{4}).*", line)
    #        get the times cited from search result
    #        if re.search("(?<=TC )[0-9]{3,5}", line):
    #            i =i+1
    #        g = re.search("(?<=TC )[0-9]{3,5}", line)        
            if g:
#                print(g.group())
                l.append(g.group())
#                    f.writelines(g.group()+'\n')
                i=i+1
    finally:
         file_object.close()
         print(i,'            ',a)  
    return l

def DOI_find_highpaper():
    l = []
    i = 0
    file_object = open('WOS_list\\savedrecs.ciw','rU', encoding='UTF-8')
    try:
        for line in file_object:
            g = re.search("(?<=TI ).*$", line)     
            if g:
                l.append(g.group())
                i=i+1
    finally:
         file_object.close()
         with open("highly_cited_paper.txt", 'w') as f:
             for word in l:
                 f.write(word+"\n")
    return l

def PLOS_get(l,a):
    i = 0    
    for ids in l:
        try:
            url = "http://journals.plos.org/plosone/article/file?id="+ids+"&type=manuscript"
            i=i+1
            req = Request(url)
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
            html = urlopen(req)
            name=str(a)+'\\'+str(i)+".xml"
            folder = os.path.exists(str(a))
            if not folder:      
                os.makedirs(str(a))
            with open(name, 'wb') as f:
                f.write(html.read())
                print(ids,"               ",name)
                time.sleep(1)
        except URLError as e:
            with open("error.log",'a') as f:
                f.write(str(a)+"/"+str(i)+"    "+str(e.code)+"    "+str(ids)+'\n')
            print("error:"+str(a)+"\\"+str(i)+"    "+str(e.code)+"    "+str(ids))
            pass
        
def PLOS_revise(ids,a,i):
    try:
        url = "http://journals.plos.org/plosone/article/file?id="+ids+"&type=manuscript"
        req = Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
        html = urlopen(req)
        name=str(a)+'\\'+str(i)+".xml"
        folder = os.path.exists(str(a))
        if not folder:      
            os.makedirs(str(a))
        with open(name, 'wb') as f:
            f.write(html.read())
            print(ids,"               ",name)
            time.sleep(1)
    except URLError as e:
        with open("error.log",'a') as f:
            f.write(str(a)+"/"+str(i)+"    "+str(e.code)+"    "+str(ids)+'\n')
        print("error:"+str(a)+"\\"+str(i)+"    "+str(e.code)+"    "+str(ids))
        pass

def xml_find_loc(i,target):
    files= os.listdir("Citation_paper\\" + str(i))
    for file in files:
        print(files + '\\' + file)
        titles = {}
        rid_real = ''
        location = ''
        try:
            tree = ET.ElementTree(file = "Citation_paper\\" + str(i)+ "\\" + file)
            root = tree.getroot()
            for elm in tree.iter("ref"):
                if(elm.find(".//article-title") != None):
    #                    rid = elm.attrib['id'] 
                    f_title = elm.find(".//article-title").text.lower()
                    titles[f_title] = elm.attrib['id']
            rid_real = edit_distance(target,titles)
            print(rid_real)
            for sec in root[1]:
                for s in sec:
                    if(s.tag == 'p'):                                                                   
                        for ss in s:
                            if(ss.tag == 'xref' and ss.attrib['rid'] == rid_real):
                                location = sec[0].text
            if (location == ''):
                print("No in-text citation!")
            else:
                print(location)
        except Exception as e:
            print('Reason:', e) 
        print('------------------------------------------------------------------------')
#    return location

def edit_distance(target,titles):
    rid_real = ''
    distance0 = 50
    for title in titles.items():
        if (distance.levenshtein(target, title[0]) < distance0):
            distance0 = distance.levenshtein(target, title[0])
            rid_real = title[1]
    return rid_real

#def title_preprocessing(text):
#    punc = str.maketrans({key: ' ' for key in string.punctuation})
#    trans = str(text).translate(punc).lower()  
#    tokens = nltk.word_tokenize(trans)
#    porter = nltk.PorterStemmer()
#    stemmed = [porter.stem(word) for word in tokens]
#    stop_words = set(nltk.corpus.stopwords.words('english'))
#    wordlist = [w for w in stemmed if w not in stop_words]
#    return wordlist
    
'''
top 10 citations
for a in range(1,11):
    l = DOI_find(a)
    PLOS_get(l,a)
'''

'''
manually revision with error.log
PLOS_revise("10.1371/journal.pone.0186461",9,12)
PLOS_revise("10.1371/journal.pone.0186943",1,113)
PLOS_revise("10.1371/journal.pone.0176993",1,149)
PLOS_revise("10.1371/journal.pone.0197599",2,6)
'''

#xml_find_loc(l)
#wordlist = title_preprocessing("Pharmaceuticals and personal care products in the environment: agents of subtle change?")
#print(wordlist)

l = DOI_find_highpaper()
for i in range(1,11):
    xml_find_loc(i,l[i-1].lower())




