from PIL import Image
import pytesseract
import camelot
import pandas as pd 
"""
can we turn simple image into pdf and then extract table from the now accessable table???

"""

def extract_table(file_path:str,page_number:str="1") -> list[pd.DataFrame]:
    tables = camelot.read_pdf(file_path,pages=page_number)
    
    return [table.df for table in tables]


for i in range(1,5):
    
    image = Image.open(str(i)+'.png')


    #searchable pdf
    pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default



    tables = extract_table("test.pdf")

    print(str(i)," : ",tables, "\n")


    
