from img2table.document import Image

"""
(Sander Stokhof)
using img2table to do ocr
"""


"""
img2table
https://github.com/xavctn/img2table
https://betterprogramming.pub/extracting-tables-from-images-in-python-made-easy-ier-3be959555f6f
"""
#they also havve some example code for extracting tables directly from text (note that there seem to be specfic options for borderless tables)
"""
from img2table.ocr import TesseractOCR
from img2table.document import Image

# Instantiation of OCR
ocr = TesseractOCR(n_threads=1, lang="eng")

# Instantiation of document, either an image or a PDF
doc = Image(src)

# Table extraction
extracted_tables = doc.extract_tables(ocr=ocr,
                                      implicit_rows=False,
                                      borderless_tables=False,
                                      min_confidence=50)
                                      
"""

def getTable(filename,implicit_rows:bool=False,borderless_tables:bool=False,path:str = "/home/hal9000/Documents/github/CIBG-WNT-Parser/experiments/orc/") -> list:
    # Instantiation of the image
    img = Image(src=path+filename) 
    img_tables = img.extract_tables(implicit_rows =implicit_rows,borderless_tables=borderless_tables, min_confidence = 50)

    return img_tables



for i in range(1,5):

    print(getTable(str(i)+".png"))

