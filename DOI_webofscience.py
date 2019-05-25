'''
extract DOI from Web of Science file
'''

import re
import os
import time
from urllib.request import urlopen,Request
from urllib.error import URLError

def DOI_find(a):
    l = []
    file_object = open('savedrecs ('+str(a)+').ciw','rU', encoding='UTF-8')
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
    
#for a in range(1,11):
#    l = DOI_find(a)
#    PLOS_get(l,a)
#l = DOI_find(2)
#PLOS_get(l,2)
PLOS_revise("10.1371/journal.pone.0186461",9,12)
PLOS_revise("10.1371/journal.pone.0186943",1,113)
PLOS_revise("10.1371/journal.pone.0176993",1,149)
PLOS_revise("10.1371/journal.pone.0197599",2,6)












