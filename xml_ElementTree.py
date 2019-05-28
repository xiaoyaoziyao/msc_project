# -*- coding: utf-8 -*-
"""
use pdfminer to get the data

"""
import re
import xml.etree.ElementTree as ET
import distance

def find_loc(i,a,target):
    titles = {}
    location = ''
    rid = ''
    try:
        file = 'Citation_paper\\' + str(i) + '\\' + str(a) + ".xml"
        tree = ET.ElementTree(file = file)
        body = tree.getroot().find('.//body')
        for elm in tree.iterfind('.//ref'):      
            if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None):
                f_title = elm.find(".//article-title").text
                titles[f_title] = elm.attrib['id']
        rid_real = edit_distance(target,titles)
        for sec in body:
            for ref in sec.iterfind('.//xref'):
                if(ref != None and ref.attrib["rid"] == rid_real):
                    location = sec[0].text
                    print(location)
        if(rid_real == ''):
            print("#Cannot find reference id!!!")
        if(location == ''):
            print("#Cannot find in-text citation!!!")
    except Exception as e:
        print('Reason:', e) 
    print('------------------------------------------------------------------------')
#    return location
def edit_distance(target,titles):
    rid_real = ''
    distance0 = distance.levenshtein(target, list(titles.keys())[0])
    for title in titles.items():       
        if (distance.levenshtein(target, title[0]) <= distance0):
            distance0 = distance.levenshtein(target, title[0])
            rid_real = title[1]
    return rid_real
#for a in range(1,12):
#    print(a)
find_loc(2,11,"Positive psychology - An introduction")
#print(location)

'''
highly-cited paper for different topic (typo problem!!!) proximity search!!!
'''
#a="<\itelic>wdewfew"
#g = re.search('[<][\a-zA-Z0-9]+[>]',a)
#print(g)
#print(a.replace(g.group(),''))