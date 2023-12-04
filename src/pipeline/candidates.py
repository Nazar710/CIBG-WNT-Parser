# pdf to list of strings(1 string per page)
# doesn't work with scanned PDFs
# https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
from typing import Any
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pandas as pd
import numpy as np
import os
from ocr_main import OCRMain

class CandidatePages:
    # pdf to list of strings(1 string per page)
    # doesn't work with scanned PDFs
    
    # constructor method

    def __init__(self, keywords=["bezoldiging", "wnt"]):   
        
        self.keywords = keywords




    def get_candidates(self, pdf_path="Type3.pdf"):
        pages = self.extract_pages_as_strings(pdf_path)
        if not self.scannCheck(pages):
            pages = OCRMain.on_file(pdf_path)
        candidates = self.find_candidates(pages, self.keywords)
        return candidates

        
    def extract_pages_as_strings(self,pdf_filename):
        resource_manager = PDFResourceManager()
        pages_content = []

        for page in PDFPage.get_pages(open(pdf_filename, 'rb')):
            fake_file_handle = StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            pages_content.append(text)
            converter.close()
            fake_file_handle.close()

        return pages_content

    # check if pages contain text
    def scannCheck(self,pages):
        for page in pages[0]:
            if page == "\x0c":
                return False
        return True

    # simple approach with 'in' operator
    # returns list of page numbers where both keywords are present

    def find_candidates(self,pages, keywords):   
        candidates = []
        for i,text in enumerate(pages):
            contains_all_keywords = all(keyword.lower() in text.lower() for keyword in keywords)
            if contains_all_keywords:
                candidates.append(i)
        return candidates        
            
if __name__ == "__main__":
    getcandidates = CandidatePages()
    print(getcandidates.get_candidates(r"C:\Users\noahc\PycharmProjects\CIBG-WNT-Parser\dataProcessing\Type2-scan.pdf"))
