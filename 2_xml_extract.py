"""
Acquire XML files according to DOIs(every 10 cited papers as a unit and stored in a file)
"""
from urllib.request import urlopen, Request
from urllib.error import URLError
import pymongo
import os


def plos_get(path, collection, i):
    """
    Acquire XML files of citation papers from PLOS, meanwhile record the error in "error.log"
    """
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10, '$lte': i*10}})
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
            req.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
            html = urlopen(req)
            name = path + "\\" + str(j) + ".xml"
            collection.update_one({'doi_link': link, 'cited_no': cited_no}, {'$set': {'content_path': name}})
            with open(name, 'wb') as f:
                f.write(html.read())
                print(link, "               ", name)
        except URLError as e:
            with open(path + "\\error.log", 'a') as f:
                f.write(str(j)+"    "+str(link)+"    "+str(e.code)+'\n')
            pass


def plos_modify(t_links, path, collection):
    """
    According to "error.log", modify DOI manually and  get the rest of XML files of citations from PLOS
    """
    f_links = []
    f_nos = []
    with open(path + "//error.log", 'r') as f:
        f = f.readlines()
        for line in f:
            f_nos.append(line.split("    ")[0])
            f_links.append(line.split("    ")[1])
    for i in range(len(t_links)):
        url = "http://journals.plos.org/plosone/article/file?id="+t_links[i]+"&type=manuscript"
        req = Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
        html = urlopen(req)
        name = path + "\\" + str(f_nos[i]) + ".xml"
        collection.update_many({'doi_link': f_links[i]}, {'$set': {'doi_link': t_links[i], 'content_path': name}})
        with open(name, 'wb') as f:
            f.write(html.read())
            print(t_links[i], "               ", name)


def main_function(i):
    """
    Main function
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    path = "Citation_paper\\"+str(i)
    plos_get(path, collection, i)


def main_modify(i, t_links):
    """
    Main modification for wrong DOIs, correct DOIs and serial number of the unit are required
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    path = "Citation_paper\\"+str(i)
    plos_modify(t_links, path, collection)


"""
Main function
"""
for i in range(1,12):
    main_function(i)

t_links1 = ["10.1371/journal.pone.0186943","10.1371/journal.pone.0176993",
"10.1371/journal.pone.0197599","10.1371/journal.pone.0186461"]
t_links2 = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0180444"]
t_links3 = ["10.1371/journal.pone.0063671","10.1371/journal.pone.0180444","10.1371/journal.pone.0188859"]
t_links4 = ["10.1371/journal.pone.0191207","10.1371/journal.pone.0162564"]
t_links5 = ["10.1371/journal.pone.0187044"]
t_links6 = ["10.1371/journal.pone.0187044"]
t_links7 = ["10.1371/journal.pone.0177179"]
t_links8 = ["10.1371/journal.pone.0204714","10.1371/journal.pone.0181873",
"10.1371/journal.pcbi.0030141","10.1371/journal.pcbi.0020165"]
t_links9 = ["10.1371/journal.pone.0176993","10.1371/journal.pone.0191812"]
t_links10 = ["10.1371/journal.pcbi.0020165","10.1371/journal.pone.0208196"]
t_links11 = ["10.1371/journal.pone.0186168", "10.1371/journal.pone.0197103"]
main_modify(1,t_links1)
main_modify(2,t_links2)
main_modify(3,t_links3)
main_modify(4,t_links4)
main_modify(5,t_links5)
main_modify(6,t_links6)
main_modify(7,t_links7)
main_modify(8,t_links8)
main_modify(9,t_links9)
main_modify(10,t_links10)
main_modify(11,t_links11)
