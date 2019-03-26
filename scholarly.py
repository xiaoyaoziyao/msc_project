'''
use scholarly to find the citation ---unfinished
'''

import scholarly

search_query = scholarly.search_pubs_query('10.1038/NMETH.2019')
print(next(search_query))

#search_query = scholarly.search_author('Marty Banks, Berkeley')
#print(next(search_query))
#print([pub.bib['title'] for pub in author.publications])
#pub = author.publications[0].fill()
#print([citation.bib['title'] for citation in pub.get_citedby()])