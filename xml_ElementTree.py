# -*- coding: utf-8 -*-
"""
use pdfminer to get the data

"""
import re
import xml.etree.ElementTree as ET
def find_loc(i,a,title):
    location = ''
    rid = ''
    try:
        file = 'Citation_paper\\' + str(i) + '\\' + str(a) + ".xml"
        tree = ET.ElementTree(file = file)
        body = tree.getroot().find('.//body')
        for elm in tree.iterfind('.//ref'):      
            if(elm.find('.//article-title') != None and elm.find('.//article-title').text != None and title in elm.find('.//article-title').text.lower()):
                print(elm.find('.//article-title').text)
                rid = elm.attrib['id']  
                print(rid)
        for sec in body:
            for ref in sec.iterfind('.//xref'):
                if(ref != None and ref.attrib["rid"] == rid):
                    location = sec[0].text
                    print(location)
        if(location == ''):
            print("#Cannot find in-text citation!!!")
    except Exception as e:
        print('Reason:', e) 
    print('------------------------------------------------------------------------')
#    return location
for a in range(1,12):
    print(a)
    find_loc(5,a,"agent")
#print(location)

'''
highly-cited paper for different topic (typo problem!!!) proximity search!!!
'''
#a="<\itelic>wdewfew"
#g = re.search('[<][\a-zA-Z0-9]+[>]',a)
#print(g)
#print(a.replace(g.group(),''))