'''
extract DOI from Web of Science file
'''

import re
 
file_object = open('E:\Download\savedrecs.ciw','rU', encoding='UTF-8')
f = open('out.txt','w', encoding='UTF-8')
#i=0
try:
    for line in file_object:
        g = re.search("(?<=DI )10\.([0-9]{4}).*", line)
#        get the times cited from search result
#        if re.search("(?<=TC )[0-9]{3,5}", line):
#            i =i+1
#        g = re.search("(?<=TC )[0-9]{3,5}", line)        
        if g:
            print(g.group())
            f.writelines(g.group()+'/n')
finally:
     file_object.close()
     
#print(i)