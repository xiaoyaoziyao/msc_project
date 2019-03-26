'''
use plos to get the paper
'''

import requests

def getPage(ids,API_KEY):
    baseurl = "http://api.plos.org/search?q=reference:'non+Watson+Crick'&fl=id" 
    param = 'ids:' + '10.1371%s2Fjournal.pone.%s'%("%",ids) + '&api_key:' + API_KEY
    r = requests.get(baseurl)
    return r.text

print(getPage("0001543","9yaXEsAZxuBfUX_i42Wg"))