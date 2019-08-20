"""
Generate word cloud
"""
import pymongo
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from tika import parser
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from PIL import Image
import numpy as np
from os import path
from collections import Counter


def Preprocessing(text):
    """
    Tokenization, punctuation removing, stopwords removing
    """
    text = text.lower()
    for c in string.punctuation:
        text = text.replace(c," ")
    wordlist = nltk.word_tokenize(text)
    filtered = [w for w in wordlist if w not in stopwords.words('english')]
    # ps = PorterStemmer()
    # filtered = [ps.stem(w) for w in filtered]
    wl = WordNetLemmatizer()
    filtered = [wl.lemmatize(w) for w in filtered]
    return filtered


def xml_find_title(collection):
    """
    Find the titles of citation papers from their XML files
    """
    cursor = collection.find()
    for docu in cursor:
        path = docu["content_path"]
        try:
            tree = ET.ElementTree(file=path)
            title = tree.getroot().find('.//article-title').text
            print(title)
            collection.update_one({'content_path': path}, {'$set': {'citation_title': title}})
        except Exception as e:
            pass
            print(path, 'Reason:', str(e), '\n')


def plos_find_title(collection):
    """
    Find the titles of citation papers through PLOS API as a supplement for xml_find_title(collection)
    """
    cursor = collection.find({'$or': [{"citation_title": {"$exists": False}}, {"citation_title": None}]})
    for docu in cursor:
        ids = docu["doi_link"]
        url = "http://api.plos.org/search?q=" + ids + "&fl=title"
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
        result = str(urlopen(req).read(), encoding="utf-8")
        result = result.split('\"')[-2]
        print(result)
        collection.update_many({'doi_link': ids}, {'$set': {'citation_title': result}})


def get_title_i(collection,i):
    """
    Get titles of citation papers from database and connect them together as a string
    """
    cursor = collection.find({'$and': [{"cited_no": i}, {"citation_title": {"$exists": True}},
                                       {"citation_title": {"$ne": None}}]})
    titles = ""
    for docu in cursor:
        titles += docu["citation_title"]
        # cited_title = docu["cited_title"]
    # print(cited_title)
    return titles


def get_title_year(collection, a, b):
    """
    Get titles of citation papers and cited papers in a particular period
    """
    cursor = collection.find({'$and': [{"cited_year": {"$gt": a, "$lte": b}},
                                       {"citation_title": {"$exists": True}}, {"citation_title": {"$ne": None}}]})
    titles = ""
    cited_titles = []
    count_title = 0
    for docu in cursor:
        titles += docu["citation_title"]
        count_title += 1
        cited_title = docu["cited_title"]
        if(cited_title not in cited_titles):
            cited_titles.append(cited_title)
    cited = " ".join(cited_titles)
    # draw_cloud(cited)
    citeds = Preprocessing(cited)
    counter = Counter(citeds)
    # dictionary = dict(counter)
    print(len(citeds))
    print(count_title)
    for i in counter.most_common(20):
        print(i)
    return titles


def draw_cloud(titles):
    """
    Generate word cloud with the string
    """
    word_list = Preprocessing(titles)
    text = " ".join(word_list)
    # counter = Counter(word_list)
    # dictionary = dict(counter)
    mask = np.array(Image.open("image.png"))
    wc = WordCloud(scale=4, width=200, height=100, background_color="white", max_words=2000,
                   mask=mask, contour_width=10, contour_color='steelblue')
    wc_text = wc.generate(text)
    # wc_text = wc.generate_from_frequencies(dictionary)
    plt.imshow(wc_text, interpolation='bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()


"""
Main function
"""
client = pymongo.MongoClient('localhost:27017', connect=True)
db = client['msc_project']
collection = db['citations']
xml_find_title(collection)
plos_find_title(collection)
titles = get_title_i(collection, 3)
titles = get_title_year(collection, 2006, 2019)
draw_cloud(titles)