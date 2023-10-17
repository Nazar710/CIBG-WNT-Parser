from PIL import Image
import pytesseract
import tabula
import pandas as pd 



 
image = Image.open("5.jpeg")


#searchable pdf
pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
with open('test.pdf', 'w+b') as f:
    f.write(pdf) # pdf type is bytes by default



tables = tabula.read_pdf("test.pdf", pages="all")


print(tables)


    
