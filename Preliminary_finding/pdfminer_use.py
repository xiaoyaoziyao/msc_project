'''
use pdfminer3k to get the data
'''


# from pdfminer.pdfparser import PDFParser, PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.converter import PDFPageAggregator
# from pdfminer.layout import LAParams, LTTextBox, LTTextLine
#
# fp = open('F:\Project Preparation\msc_project\journal.pcbi.1003897.PDF', 'rb')
# parser = PDFParser(fp)
# doc = PDFDocument()
# parser.set_document(doc)
# doc.set_parser(parser)
# doc.initialize('')
# rsrcmgr = PDFResourceManager()
# laparams = LAParams()
# laparams.char_margin = 1.0
# laparams.word_margin = 1.0
# device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# interpreter = PDFPageInterpreter(rsrcmgr, device)
# extracted_text = ''
#
# for page in doc.get_pages():
#     interpreter.process_page(page)
#     layout = device.get_result()
#     for lt_obj in layout:
#         if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
#             extracted_text += lt_obj.get_text()
# # print(extracted_text)
# with open("F:\Project Preparation\msc_project\journal.pcbi.1003897.PDFtoXML.txt", 'w', encoding='utf-8') as f:
#     f.write(extracted_text)

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open
import tika
from tika import parser


def readPDF(pdfFile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    process_pdf(rsrcmgr, device, pdfFile)
    device.close()

    content = retstr.getvalue()
    retstr.close()
    return content


def saveTxt(txt):
    with open("F:\Project Preparation\msc_project\journal.pcbi.1003897.tika.txt", "w",encoding='utf-8') as f:
        f.write(txt)


# txt = readPDF(open('F:\Project Preparation\msc_project\journal.pcbi.1003897.PDF', 'rb'))
# saveTxt(txt)

file = 'F:\Project Preparation\msc_project\journal.pcbi.1003897.PDF'
# Parse data from file
file_data = parser.from_file(file)
# Get files text content
text = file_data['content']
saveTxt(text)
