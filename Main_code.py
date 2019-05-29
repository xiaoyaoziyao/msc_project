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

'''
Extract the DOI of citations
'''
def DOI_find(a):
    file_object = open('WOS_list\\savedrecs ('+str(a)+').ciw','rU', encoding='UTF-8')
    name = 'out('+str(a)+').txt'
    f = open(name,'w', encoding='UTF-8')
    i=0
    try:
        for line in file_object:
            g = re.search("(?<=DI )10\.([0-9]{4}).*", line)    
            if g:
                print(g.group())
                f.writelines(g.group()+'\n')
                i=i+1
    finally:
         file_object.close()
         print(i,'            ',a)  

'''
Extract the titles of highly-cited papers
'''
def DOI_find_highpaper():
    l = []
    m = []
    i = 0
    file_object = open('WOS_list\\savedrecs.ciw','rU', encoding='UTF-8')
    try:
        for line in file_object:
            g = re.search("(?<=TI ).*$", line)     
            y = re.search("(?<=PY ).*$", line)
            if g:
                l.append(g.group())
                i=i+1
            if y:
                m.append(y.group())
    finally:
         file_object.close()
#         with open("highly_cited_paper.txt", 'w') as f:
#             for word in l:
#                 f.write(word+"\n")
    return (l,m)

'''
Acquire the xml files of citations from PLOS ONE, meanwhile record the error in "error.log"
'''
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

'''
According to "error.log", revise the DOI manually and  get the rest of xml files of citations from PLOS ONE
'''      
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

'''
Extract the rid and location of citations from xml files
'''   
def xml_find_loc(i,target_title,target_year):
    files= os.listdir("Citation_paper\\" + str(i))
    folder = os.path.exists("Results")
    if not folder:      
        os.makedirs("Results")
    savefile = "Results\\result(" + str(i) +").txt"
    f = open(savefile,'w')
    f.write("Target_Title: " + target_title + "\n")
    f.write("Target_Year: " + target_year + "\n")
    f.write('************************************************************************\n')
    a = 0
    b = 0
    for file in files:
        if file.endswith('.xml'):
    #        print("Citation_paper\\" + str(i) + '\\' + file)
            f.write("Citation_paper\\" + str(i) + '\\' + file + '\n')
            titles = {}
            rid_real = ''
            location = []
            try:
                tree = ET.ElementTree(file = "Citation_paper\\" + str(i)+ "\\" + file)
                body = tree.getroot().find('.//body')
                year = tree.find(".//pub-date/year").text
                for elm in tree.iterfind('.//ref'):      
                    if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                        f_title = elm.find(".//article-title").text
                        titles[f_title] = elm.attrib['id']
    #            print(titles)
                rid_real = edit_distance(target_title,titles)
                if(rid_real == ''):
    #                print("#Cannot find reference id!!!")
                    f.write("#Cannot find reference id!!!\n")
                    a = a + 1
                else:
                    f.write("RId: " + rid_real + '\n')
                for sec in body:
                    for ref in sec.iterfind('.//xref'):
                        if(ref != None and ref.attrib["rid"] == rid_real):
                            location.append(sec[0].text)
                for loc in list(set(location)):
                    f.write("Location: " + loc + '\n')
                    f.write("Year_Diff: " + str(int(year)-int(target_year)) + '\n')
                if(rid_real != '' and len(location) == 0):
    #                print("#Cannot find in-text citation!!!")
                    f.write("#Cannot find in-text citation!!!\n")  
                    b = b + 1
            except Exception as e:
    #            print('Reason:', e) 
                f.write('Reason:' + str(e) + '\n')
    #        print('------------------------------------------------------------------------')
            f.write('------------------------------------------------------------------------\n')
    f.write('************************************************************************\n')
    f.write("Cannot find reference id: " + str(a) + '\n')
    f.write("Cannot find in-text citation: " + str(b) + '\n')
    f.close()
#    return location

'''
Calculate the levenshtein distance to do fuzzy match for titles
'''   
def edit_distance(target,titles):
    rid_real = ''
    distance0 = distance.levenshtein(target, list(titles.keys())[0])
    for title in titles.items():       
        if (distance.levenshtein(target, title[0]) <= distance0):
            distance0 = distance.levenshtein(target, title[0])
            rid_real = title[1]
    return rid_real


'''
Read the results.txt as lists
'''   
def read_results(i):
    Year_Diff = []
    Location = []
    savefile = "Results\\result(" + str(i) +").txt"
    with open(savefile,'r') as f:
        lines = f.readlines()
        for i in range(3,len(lines)-2):
            if(lines[i].startswith('Location:') and lines[i+1].startswith('Year_Diff:')):
                Location.append(lines[i][10:].replace('\n',''))
                Year_Diff.append(int(lines[i+1][11:].replace('\n','')))
    for k in range(len(Location)):
        print(Location[k],'           ',Year_Diff[k])
    return (Location, Year_Diff)

'''
Main function
'''
###Finished part###

##citations of top 10 highly-cited paper
#for a in range(1,11):
#    l = DOI_find(a)
#    PLOS_get(l,a)
#
##manually revision according to "error.log"
#PLOS_revise("10.1371/journal.pone.0186943",1,113)
#PLOS_revise("10.1371/journal.pone.0176993",1,149)
#PLOS_revise("10.1371/journal.pone.0197599",2,6)
#PLOS_revise("10.1371/journal.pone.0186461",9,12)
#
##Extract year and location of citations
#targets_title = DOI_find_highpaper()[0]
#targets_year = DOI_find_highpaper()[1]
#for i in range(1,11):
#    print("Highly-cited paper " + str(i) + "......")
#    xml_find_loc(i,targets_title[i-1],targets_year[i-1])
    
###Ongoing part###
for i in range(1,11):
    print(i,'----------------------------------------------')
    read_results(i)





