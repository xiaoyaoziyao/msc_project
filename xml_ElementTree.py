# -*- coding: utf-8 -*-
"""
use pdfminer to get the data

"""
import re
import xml.etree.ElementTree as ET
def find_loc(i,a,title):
    try:
        file = 'Citation_paper\\' + str(i) + '\\' + str(a) + ".xml"
        print(a)
        tree = ET.ElementTree(file = file)
        root = tree.getroot()
        for elm in tree.iter("ref"):      
            if(elm.find(".//article-title") != None and title in elm.find(".//article-title").text.lower()):
                print(elm.find(".//article-title").text)
                rid = elm.attrib['id']  
                print(rid)
        for sec in root[1]:
            for s in sec:
                if(s.tag == 'p'):
                    for ss in s:
                        if(ss.tag == 'xref' and ss.attrib['rid'] == rid):
                            location = sec[0].text                        
        print(location)
    except Exception as e:
        print('Reason:', e) 
    print('------------------------------------------------------------------------')
#    return location

for a in range(1,11):
    find_loc(5,a,"agent")
#print(location)

'''
highly-cited paper for different topic (typo problem!!!) proximity search!!!
'''
#a="<\itelic>wdewfew"
#g = re.search('[<][\a-zA-Z0-9]+[>]',a)
#print(g)
#print(a.replace(g.group(),''))