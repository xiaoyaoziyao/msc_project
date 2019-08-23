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


# Used for title standardization
stand_title = ["Others", "Introduction and Background", "Materials and Methods", "Results and Discussion", "Conclusion"]


def xml_find_loc(collection, i):
    """
    Extract the rid and location of citations from xml files
    """
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10, '$lte': i*10}})
    for docu in cursor:
        titles = {}
        location = []
        target_title = docu["cited_title"]
        path = docu["content_path"]      
        try: 
            tree = ET.ElementTree(file=path)
            body = tree.getroot().find('.//body')
            year = tree.find(".//pub-date/year").text
            collection.update_one({'content_path': path, "cited_title": target_title },
                                  {'$set': {'citation_year': int(year)}})
            for elm in tree.iterfind('.//ref'):      
                if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                    f_title = elm.find(".//article-title").text.lower()
                    titles[f_title] = elm.attrib['id']
            rid_real = edit_distance(target_title, titles)
            collection.update_one({'cited_title': target_title, 'content_path': path},
                                  {'$set': {'reference_id': rid_real}})
#            print("update path:",path,",update rid:",rid_real)
            for sec in body:
                for xref in sec.iterfind('.//xref'):
                    if(xref != None and xref.attrib["rid"] == rid_real):
                        location.append(sec[0].text)
            if(len(rid_real) != 0 and len(location) == 0):
                location = xml_find_modify(path, rid_real)
            collection.update_one({'content_path': path}, {'$set': {'cited_location': location}})
            # print("update path:", path, ",update rid:", rid_real, "cited_location", location)
        except Exception as e:
            pass
            print(path, 'Reason:', str(e), '\n')


def xml_find_modify(path, rid_real):
    """
    Modify the situation that the reference id or the location is unable to find.
    """
    location = []
    tree = ET.ElementTree(file=path)
    body = tree.getroot().find('.//body')
    for elm in tree.iterfind('.//ref'):
        if elm.attrib['id'] == rid_real:
            label = elm.find(".//label").text
    # print(label)
    for sec in body:
        xref = sec.findall('.//xref')
        for i in range(len(xref)):
            if((xref[i].tail == '-' or xref[i].tail == '–') and not re.search('[a-zA-Z]', xref[i].text)):
                # print(xref[i].tail)
                xref_text = ''.join(c for c in xref[i].text if c.isdigit())
                xref_next_text = ''.join(c for c in xref[i+1].text if c.isdigit())
                if(int(xref_text) <= int(label)  and int(xref_next_text) >= int(label)):
                    location.append(sec[0].text)
    # print(location)
    return location


def edit_distance(target, titles):
    """
    Calculate the levenshtein distance to do fuzzy match for titles
    """
    dis = []
    for title in titles.items():       
        dis.append(distance.levenshtein(target, title[0]))
    dis_index = dis.index(min(dis))
    rid_real = list(titles.values())[dis_index]
    return rid_real


def preprocess(sentence):
    """
    Preprocess the standard titles and locations to help do the comparison
    """
    tokens = [i.lower() for i in nltk.word_tokenize(sentence)]
    filtered = [word for word in tokens if word not in stopwords.words('english')]
    s = nltk.stem.SnowballStemmer('english')
    tokens = [s.stem(i) for i in filtered if i.isalpha()]
    return tokens


def compare(location):
    """
    Compare whether the words in the citation location also exist in one standard citation location
    Encode the classes for citation locations
    """
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
    return(loc, loc_num)
                

def standard_loc(collection, i):
    """
    Standardize the citation locations to help do the visualization
    """
    cursor = collection.find({'cited_no': {'$gt': (i-1)*10, '$lte': i*10}, "cited_location": {'$exists': True}})
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
                collection.update_one({'content_path': path, "cited_location": location},
                                      {'$set': {'stand_location': stand_loc, 'location_no': stand_num}})
        except Exception as e:
            pass
            print(path, 'Reason:', str(e), '\n')


def main_function(i):
    """
    Main function
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']        
    xml_find_loc(collection, i)
    standard_loc(collection, i)
    client.close() 


def main_modify():
    """
    Main modify
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    cursor = collection.find({"cited_no": {"$gt": 20}, "location_no": {"$exists": True}})
    for docu in cursor:
        content_path = docu["content_path"]
        reference_id = docu["reference_id"]
        print(content_path, reference_id)
        location = xml_find_modify(content_path, reference_id)
        if len(location) != 0:
            collection.update_one({'content_path': content_path, "reference_id": reference_id},
                                  {'$set': {'cited_location': location}})
    for i in range(1, 12):
        standard_loc(collection, i)


# for i in range(1, 12):
#     main_function(i)
# main_modify()

# Count the invalid data
client = pymongo.MongoClient('localhost:27017', connect=True)
db = client['msc_project']
collection = db['citations']
cursor = collection.find({"cited_no": {"$gt": 20}, "$or": [{"location_no": {"$exists": True}}, {"location_no": {"$ne": None}}]})
print(cursor.count())

