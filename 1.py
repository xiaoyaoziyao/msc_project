import re
import pymongo
import nltk
import string
from urllib.request import urlopen,Request
from nltk.corpus import stopwords
from urllib.error import URLError


def DOI_find_highpaper(collection):
    num = 0
    titles = []
    with open("savedrecs.ciw",'r', encoding='UTF-8') as f:
        f = f.readlines()
        i = 0
        for line in f:
            y = re.search("(?<=^PY ).*$", line)
            t = re.search("(?<=^TI ).*$", line)
            if t:
                if(f[i+1].startswith('SO')):
                    title = t.group()
                else:
                    title = t.group() + f[i+1].replace('\n','') .replace('  ','')
                num = num + 1
                collection.update_many({'cited_no': num},{'$set':{'cited_title':title}})
                titles.append(title)
            if y:
                year = y.group()
                collection.update_many({'cited_no': num},{'$set':{'cited_year':int(year)}})
            i = i + 1
    return titles


def citation_doi_get(title):
    for title in titles:
        con = urlopen("http://api.plos.org/search?q=title:"+title+"&fl=id")
        res = eval(con.read())
        for document in res['response']['docs']:
            t_link = document['id']
    return t_link

def preprocess(s):
    '''
    Preprocess the standard titles and locations to help do the comparison
    '''
    # tokens = [i.lower() for i in nltk.word_tokenize(sentence)]
    # filtered = [word for word in tokens if word not in stopwords.words('english')]
    # s = nltk.stem.SnowballStemmer('english')
    punc = str.maketrans({key: ' ' for key in string.punctuation})
    new_s = s.translate(punc)
    # tokens = [i for i in tokens if i.isalpha()]
    # result = ' '.join(tokens)
    return new_s

client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations_update']
titles = DOI_find_highpaper(collection)
for title in titles:
    title = preprocess(title)
    print(title)
    print("      ")
    # doi_links = citation_doi_get(title)
    # print(doi_links)