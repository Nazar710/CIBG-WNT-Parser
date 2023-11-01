from PIL import Image
import pytesseract
import camelot
import pandas as pd 


"""
(Sander Stokhof)

using camelot together with pytesseract to extract tables from jpegs
"""

def extract_table(file_path:str,page_number:str="1") -> list[pd.DataFrame]:
    """
    @param 
        file_path:string
        page_number:string (the page number)
    
    @return 
        list[pd.DataFrame] for each table 
    """
    tables = camelot.read_pdf(file_path,pages=page_number)
    
    return [table.df for table in tables]


 
image = Image.open("5.jpeg")


#searchable pdf
pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
with open('test.pdf', 'w+b') as f:
    f.write(pdf) # pdf type is bytes by default



tables = extract_table("test.pdf")

print(tables)


    
