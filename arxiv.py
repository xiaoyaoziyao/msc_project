'''
use arxiv to get the paper
'''

import requests
url = 'http://export.arxiv.org/api/query?search_query=jr:Mod. Phys.'
data = requests.get(url)
print(data.text)

#import urllib.request
#import pandas as pd
#import xml.etree.ElementTree as ET
#
#OAI = "{http://www.openarchives.org/OAI/2.0/}"
#ARXIV = "{http://arxiv.org/OAI/arXiv/}"
#
#def harvest(arxiv):
#    df = pd.DataFrame(columns=("title", "abstract", "categories"))
#    base_url = "http://export.arxiv.org/oai2?verb=ListRecords&"
#    url = (base_url +
#           "from=2012-01-01&until=2019-01-01&" +
#           "metadataPrefix=arXiv&set=%s"%arxiv)
#
#    while True:
#        print("fetching", url)
#
#        response = urllib.request.urlopen(url)
#
#        xml = response.read()
#
#        root = ET.fromstring(xml)
#
#        for record in root.find(OAI+'ListRecords').findall(OAI+"record"):
#            meta = record.find(OAI+'metadata')
#            info = meta.find(ARXIV+"arXiv")
#            categories = info.find(ARXIV+"categories").text
#
#            contents = {'title': info.find(ARXIV+"title").text,
#                        'abstract': 
#                         info.find(ARXIV+"abstract").text.strip(),
#                        'categories': categories.split(),
#                        }
#
#            df = df.append(contents, ignore_index=True)
#
#        token = root.find(OAI+'ListRecords').find(OAI+"resumptionToken")
#        if token is None or token.text is None:
#           break
#        else:
#           url = base_url + "resumptionToken=%s"%(token.text)
#
#    return df
#
#df_hep_th = harvest("physics:hep-th")
#
#df_hep_th.to_csv('df_hep_th.csv', sep=',', encoding='utf-8')