# -*- coding: utf-8 -*-
"""
use pdfminer to get the data

"""

import xml.etree.ElementTree as ET
i = 0
tree = ET.ElementTree(file='1\\1.xml')
root = tree.getroot()
for elm in tree.iter("ref"):      
    if(elm.find(".//article-title") != None and elm.find(".//article-title").text == "Introductory science and mathematics education for 21st-century biologists"):
        doi = elm.attrib['id']  
        print(doi)
for sec in root[1]:
    for s in sec:
        if(s.tag == 'p'):
            for ss in s:
                if(ss.tag == 'xref' and ss.attrib['rid'] == doi):
                    location = sec[0].text
print(location)