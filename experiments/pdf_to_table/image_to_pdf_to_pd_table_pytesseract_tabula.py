from PIL import Image
import pytesseract
import tabula
"""
can we turn simple image into pdf and then extract table from the now accessable table???

"""

for i in range(1,5):
    
    image = Image.open(str(i)+'.png')


    #searchable pdf
    pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default



    tables = tabula.read_pdf("test.pdf", pages="all")

    print(str(i)," : ",tables, "\n")



