from PIL import Image
import pytesseract
import tabula
import pandas as pd 

"""
(Sander Stokhof)

using pytesseract together with tabula to turn jpeg into table (but specifically test for wnt example)
"""

 
image = Image.open("5.jpeg")


#searchable pdf
pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
with open('test.pdf', 'w+b') as f:
    f.write(pdf) # pdf type is bytes by default



tables = tabula.read_pdf("test.pdf", pages="all")


print(tables)


    
