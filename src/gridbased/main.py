import pdfplumber 
import pandas as pd 
import matplotlib.pyplot as plt 
import Levenshtein
import thefuzz
import os 
from typing import Generator
import pandas as pd 
from functools import partial
import numpy as np 

class table_format():
    def __init__(self,table:pdfplumber.table.Table,page:pdfplumber.page.Page) -> None:
        self._table = table 
        self._page = page 

    def table(self) -> pd.DataFrame:
        return pd.DataFrame(self._table.extract())

    def debug(self) -> None:
        im = self._page.to_image()
        im.debug_tablefinder().show()


class extractor():
    """
    extractor for gridbased and free text
    """
    def __init__(self,path:str) -> None:
        self.path = path 

    def extract_text(self,page_nums:list=None,x_tolerance=3, y_tolerance=3, layout=False, x_density=7.25, y_density=13) -> list[str]:
        """
        returns text found on a page
        """
        with pdfplumber.open(self.path) as file:

            if(page_nums is not None):
                return [file.pages[page_num].extract_text(x_tolerance=x_tolerance, y_tolerance=y_tolerance, layout=layout, x_density=x_density, y_density=y_density) for page_num in page_nums]
            else:
                return [page.extract_text(x_tolerance=x_tolerance, y_tolerance=y_tolerance, layout=layout, x_density=x_density, y_density=y_density) for page in file.pages]

    def extract_gridbased(self,table_settings:dict={},page_nums:list=None) -> list[table_format]:
        """
        extracts table and keeps reference to the page it came from
        """
        with pdfplumber.open(self.path) as file:
            if(page_nums is not None):
                return [table_format(table=table,page=file.pages[page_num]) for page_num in page_nums for table in file.pages[page_num].find_tables(table_settings=table_settings)] 
            else:
                return [table_format(table=table,page=page) for page in file.pages for table in page.find_tables(table_settings=table_settings)]
                         
    def __call__(self,path:str) -> None:
        """
        update the path (that is used to extract the file)
        """
        self.path = path 
        return self



def tableListToDataFrameList(table_list:list[table_format]) -> list[pd.DataFrame]:
    return [table.table() for table in table_list]


def isInTableElement(table_elem:str,targetWord:str,threshold:float) -> bool:
    # print("table_elem: ",table_elem) 
    # print("targetWord: ",targetWord)
    # print("threshold: ",threshold)
    """
    TODO use fuzzy and alignment (with treshold) instead of naive matching
    """

    if(table_elem is None):
        return False
    else:
        return targetWord in table_elem

def findInTable(table:pd.DataFrame,targetWord:str,threshold:float) -> tuple[np.array,np.array]: #returns (xpos_array,ypos_array)
    """
    tries to find the alignment with a targetword and use fuzzy matching to see how similar the words are.
    fuzzy matching has a value in range [0,1].
    it's more than the threshold we will accept that there is word at that position.

    returns (xpos_Array,ypos_Array) for each element in the table that is in the right format
    """
    masked_table = table.map(partial(isInTableElement,threshold=threshold,targetWord=targetWord)).to_numpy()

    return masked_table.nonzero()


def findtable(table_list:list[table_format]):
    table_list = tableListToDataFrameList(table_list)    
    
    for table in table_list:

        findInTable(table,"Gegevens 2020",threshold=0.5)

        exit() #TODO remove when findInTable and dependencies are done


def pathIterator(directory_files:str="example_pdfs",accepted_formats:list[str]=["pdf"]) -> Generator:
    """
    returns an iterator for all the file paths to a directory
    """
    root_path = os.path.join(os.curdir,directory_files)
    for file_path in os.listdir(root_path):
        if(file_path.split(".")[-1] in accepted_formats):
            yield os.path.join(root_path,file_path)


if __name__ == "__main__":
    table_page_numbers = {"wnt_grid.pdf":[39,40],"wnt_grid2.pdf":[35,36]}    
    
    for path in pathIterator():
        current_filename =path.split("/")[-1]
        if(current_filename in table_page_numbers.keys()):
            table_list = extractor(path).extract_gridbased(page_nums=table_page_numbers[current_filename])

            findtable(table_list)
            
