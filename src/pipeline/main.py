import pandas as pd 
from typing import Any
from gridbased import table_extractor,table_analyser
from candidates import CandidatePages
from tqdm import tqdm 

class WNT_analyser():
    def __init__(self,download_spacy:bool,gridtable_settings:dict={}) -> None:
        self.table_analyser = table_analyser(download_spacy)
        self.table_extractor = table_extractor(table_settings=gridtable_settings)
        self.candidate_pages = CandidatePages()

    def __call__(self, folder_name:str,**kwargs) -> pd.DataFrame:
        """
        processes the wnt files and returns a joined DataFrame with
            columns:
                name
                bezoldiging
                year 
                page
                file
        """
        full_wntInfoTable = pd.DataFrame({"name":[],"bezoldiging":[],"year":[],"page":[],"file":[]}) 

        for path,file_name in tqdm(self.table_extractor.recursiveFilePathIterator(folder_name,**kwargs),ascii=True):
            print(path)

            #WNT page detector
            #....
            wnt_pages = self.candidate_pages.get_candidates(path)
            print("suggested_pages: ",wnt_pages)

            #gridbased 
            extracted_tables, pages = self.table_extractor.extract_table(path,page_nums=wnt_pages) #TODO provide page_nums
            wntInfoTable = self.table_analyser.extractWNTInfo(extracted_tables,pages,file_name)
            full_wntInfoTable = pd.concat((full_wntInfoTable,wntInfoTable),ignore_index=True)

 
        print(full_wntInfoTable)
        return full_wntInfoTable

"""
NOTE GENERAL
make sure the terminal is in the work directory of the target folder


NOTE IMPLEMENTATION
1. Get all file paths from a specified folder. (get all pdfs)
2. extract free text (with OCR and text)
3. John code find wnt pages (takes the free text step 2)
4. NER names list (from step 2)
5. methods (returns wnt info)
    a. gridbased takes (file name and page from step 3) 
    b. coordinate based wnt extractor (NER names list step 4, file name step 1, wnt page number step 2)     
    c. free text (step 2, NER names list step 4 (optional), step 3 page numbers)
6. merge all wnt info and compare with the ground truth (measure accuracy, precision, recall, f1 score)


wnt info:
    type: pd.Dataframe
    one example: 
    pd.DataFrame({"name":[name],"bezoldiging":[bezoldiging],"year":[str(current_year)],"page":[str(page_num)],"file":[file_name]}

    columns:
    name
    bezoldiging
    year 
    page
    file

step 2 notes:
    try both orc and free text extraction and find out how to perfectly mix the results for 3.

"""


if __name__ == "__main__":
    #general settings 
    download_spacy = False
    folder_name = ""
    #method
    WNT_analysor = WNT_analyser(download_spacy) 
    WNT_analysor("sorted",accepted_formats=["txt","pdf"])