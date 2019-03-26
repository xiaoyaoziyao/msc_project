'''
extract DOI from Web of Science file
'''

import re
 
file_object = open('E:\Download\savedrecs (1).txt','rU', encoding='UTF-8')
f = open('out.txt','w', encoding='UTF-8')
try:
    for line in file_object:
        g = re.search("(?<=DI )10\.([0-9]{4}).*", line)
        if g:
            print(g.group())
            f.writelines(line)
finally:
     file_object.close()