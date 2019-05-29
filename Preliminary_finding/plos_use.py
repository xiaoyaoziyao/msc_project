'''
use plos to get the paper
'''

#import requests
#
#def getPage(ids,API_KEY):
#    baseurl = "http://alm.plos.org/api/v5/articles" 
#    reqparam = { 'ids' : '10.1371%s2Fjournal.pone.%s'%("%",ids), 'info' : 'detail' ,'api_key' : API_KEY}
#    r = requests.get(baseurl, params = reqparam)
#    return r.text
#
#f = open('out1.txt','w', encoding='UTF-8')
#f.write(getPage("0001543","9yaXEsAZxuBfUX_i42Wg"))
#f.close()

import requests
import sys
import json
import pickle
import re
import time
import numpy as np

def getPage(ids,API_KEY):
    baseurl = " http://api.plos.org/search" 
    reqparam = { 'ids' : '10.1371%s2Fjournal.pone.%s'%("%",ids), 'type' : 'manuscript' ,'api_key' : API_KEY}
    r = requests.get(baseurl, params = reqparam)
    return r.text

def flatten_json(y):
    """
    hacked to accept unicode
    """
    out = {}
 
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_') 
                i += 1
        else:
            out[str(name[:-1])] = str(x)
 
    flatten(y)
    return out


print(flatten_json(getPage("0001543","9yaXEsAZxuBfUX_i42Wg")))