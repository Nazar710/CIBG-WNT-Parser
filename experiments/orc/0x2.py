from img2table.document import Image
"""
img2table
https://betterprogramming.pub/extracting-tables-from-images-in-python-made-easy-ier-3be959555f6f
"""


def getTable(filename,path = "/home/hal9000/Documents/github/CIBG-WNT-Parser/experiments/orc/"):
    # Instantiation of the image
    img = Image(src=path+filename) 
    img_tables = img.extract_tables()

    return img_tables







print(getTable("3.png"))