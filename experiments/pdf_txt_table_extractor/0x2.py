from PIL import Image
import pytesseract
import tabula
"""
can we turn simple image into pdf and then extract table from the now accessable table???

"""

image = Image.open('4.png')


print(pytesseract.image_to_boxes(image)) #gives the location of items

#searchable pdf
pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
with open('test.pdf', 'w+b') as f:
    f.write(pdf) # pdf type is bytes by default



tables = tabula.read_pdf("test.pdf", pages="all")

tables[0].head(10)

"""
no this doesnt work.
"""