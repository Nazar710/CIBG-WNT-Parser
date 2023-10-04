import camelot
import pandas as pd
"""
https://camelot-py.readthedocs.io/en/master/
https://pypi.org/project/tabula-py/
pip install camelot-py[cv] tabula-py

https://thepythoncode.com/article/extract-pdf-tables-in-python-camelot


PyPDF2.errors.DeprecationError: PdfFileReader is deprecated and was removed in PyPDF2 3.0.0. Use PdfReader instead.
https://github.com/camelot-dev/camelot/issues/339

pip install PyPDF2~=2.0 #this fixes the above bug
"""

def extract_table(file_path:str,page_number:str="1") -> list[pd.DataFrame]:
    tables = camelot.read_pdf(file_path,pages=page_number)
    
    return [table.df for table in tables]

file_path = "example_tables.pdf"

print(extract_table(file_path,"2"))

