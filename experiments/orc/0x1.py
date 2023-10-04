from PIL import Image
import pytesseract
import matplotlib.pyplot as plt 
"""
https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i

see install section:
https://pypi.org/project/pytesseract/

pip install tesseract
pip install tesseract-ocr
sudo apt-get install tesseract-ocr #(for linux)
"""

image = Image.open('1.png')


print(pytesseract.image_to_boxes(image)) #gives the location of items

#searchable pdf
pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
with open('test.pdf', 'w+b') as f:
    f.write(pdf) # pdf type is bytes by default


