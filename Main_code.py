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
def DOI_find(a):
    file_object = open('WOS_list\\2\\savedrecs ('+str(a)+').ciw','rU', encoding='UTF-8')
    name = 'DOI_list\\2\\out('+str(a)+').txt'
    f = open(name,'w', encoding='UTF-8')
    i=0
    l=[]
    try:
        for line in file_object:
            g = re.search("(?<=DI )10\.([0-9]{4}).*", line)    
            if g:
                print(g.group())
                l.append(g.group())
                f.writelines(g.group()+'\n')
                i=i+1
    finally:
         file_object.close()
         print(i,'            ',a)  
    return l

'''
Extract the titles of highly-cited papers
'''
def DOI_find_highpaper():
    l = []
    m = []
    file_object = open('WOS_list\\2\\savedrecs.ciw','rU', encoding='UTF-8')
    try:
        i = 0
        f_read = file_object.readlines()
        for line in f_read:
            y = re.search("(?<=PY ).*$", line)
            g = re.search("(?<=TI ).*$", line)
            if g:
                if(f_read[i+1].startswith('SO')):
                    title = g.group()
                else:
                    title = g.group() + f_read[i+1].replace('\n','') .replace('  ','')  
                l.append(title)
            if y:
                m.append(y.group())
            i = i+1
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
            folder = os.path.exists("Citation_paper\\2\\"+str(a))
            if not folder:      
                os.makedirs("Citation_paper\\2\\"+str(a))
            name="Citation_paper\\2\\"+str(a)+"\\"+str(i)+".xml"
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
        name="Citation_paper\\2\\"+str(a)+"\\"+str(i)+".xml"
        folder = os.path.exists("Citation_paper\\2\\"+str(a))
        if not folder:      
            os.makedirs("Citation_paper\\2\\"+str(a))
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
    files= os.listdir("Citation_paper\\2\\" + str(i))
    folder = os.path.exists("Results")
    if not folder:      
        os.makedirs("Results")
    savefile = "Results\\2\\result(" + str(i) +").txt"
    f = open(savefile,'w')
    f.write("Target_Title: " + target_title + "\n")
    f.write("Target_Year: " + target_year + "\n")
    f.write('************************************************************************\n')
    a = 0
    b = 0
    target_title = target_title.lower()
    for file in files:
        if file.endswith('.xml'):
    #        print("Citation_paper\\" + str(i) + '\\' + file)
            f.write("Citation_paper\\2\\" + str(i) + '\\' + file + '\n')
            titles = {}
            rid_real = ''
            location = []
            try:
                tree = ET.ElementTree(file = "Citation_paper\\2\\" + str(i)+ "\\" + file)
                body = tree.getroot().find('.//body')
                year = tree.find(".//pub-date/year").text
                for elm in tree.iterfind('.//ref'):      
                    if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                        f_title = elm.find(".//article-title").text.lower()
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
                    for xref in sec.iterfind('.//xref'):
                        if(xref != None and xref.attrib["rid"] == rid_real):
                            location.append(sec[0].text)
                if(len(location) == 0):
                    xml_find_revise(tree,body,rid_real,location)
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
                print(file,'Reason:', str(e), '\n')
    #        print('------------------------------------------------------------------------')
            f.write('------------------------------------------------------------------------\n')
    f.write('************************************************************************\n')
    print('Cannot find reference id: {:.2%}'.format(a/len(files)))
    print('Cannot find in-text citation: {:.2%}'.format(b/len(files)))
    f.write("Cannot find reference id: " + str(a) + '\n')
    f.write("Cannot find in-text citation: " + str(b) + '\n')
    f.close()
#    return location

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
'''   
def read_results():
    a = []
    b = []
    c = []
    d = []
    n = []
    global stand_title
    for key,value in stand_title.items():
            stand_title[key]=preprocess(value)
    print(stand_title)
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
    dataframe.to_csv("data.csv",index=False,sep=',')
    return c

def standard_loc(loc): 
    for i in loc:
        for key,value in stand_title.items():
            if i in value:
                loc = key
                break
    if loc not in range(1,7):
         loc = 0
    return loc    

def visualization(a,b,year):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title('Scatter Plot')
    plt.xlabel('Year_Diff')
    plt.ylabel('Location')
    ax1.scatter(b,a,c = 'r',marker = 'o',alpha = 0.1)
    plt.legend(str(year))
    plt.show()


'''
Main function
'''
###Finished part###

##citations of top 10 highly-cited paper
#for a in range(1,12):
#    l = DOI_find(a)
#    PLOS_get(l,a)
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

c = read_results()
data1 = pd.read_csv('data.csv')
data2 = pd.read_csv('data1.csv')
data = pd.merge(data1,data2)
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

X = list(zip(data['year_pub'],data['year_diff']+data['year_pub']))
y = data['location']
model = SVC()
score = cross_val_score(model,X,y,scoring='accuracy')
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
model.fit(X_train,y_train)
print(score.mean())


train_sizes, train_loss, test_loss = learning_curve(
    SVC(gamma=0.001), X, y, cv=10, scoring='neg_mean_squared_error',
    train_sizes=[0.1, 0.25, 0.5, 0.75, 1])
#print(train_sizes, train_loss, test_loss)
train_loss_mean = -np.mean(train_loss, axis=1)
test_loss_mean = -np.mean(test_loss, axis=1)
plt.plot(train_sizes, train_loss_mean, 'o-', color="r",
         label="Training")
plt.plot(train_sizes, test_loss_mean, 'o-', color="g",
        label="Cross-validation")
plt.xlabel("Training examples")
plt.ylabel("Loss")
plt.legend(loc="best")
plt.show()





