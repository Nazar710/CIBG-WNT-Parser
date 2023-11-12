import pdfplumber 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 
from typing import Generator
import pandas as pd 
from functools import partial
import numpy as np 
from thefuzz import fuzz
from typing import Callable

class table_format():
    """
    just a container for table and the corresponding page reference.
    """
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


class tableAnalyser():
    """
    extracts and finds targets from table.

    can use different matching functions.
    Where we look for matching for more than a certain threshold.

    optional matching functions are:
    fuzz.ratio
    fuzz.token_set_ratio

    """
    def __init__(self,matching_func:Callable=fuzz.ratio) -> None:
        self.matching_func = matching_func
         

    def isInTableElement(self,table_elem:str,targetWord:str,threshold:float) -> bool:
        if(table_elem is None):
            return False 
        
        table_elem = table_elem.lower()
        targetWord = targetWord.lower()

        if(self.matching_func(table_elem,targetWord) >= threshold):
            return True

        return False


    def findInTable(self,table:pd.DataFrame,targetWord:str,threshold:float) -> tuple[np.array,np.array]: #returns (xpos_array,ypos_array)
        """
        Use fuzzy matching to see how similar the words are.
        fuzzy matching has a value in range [0,1].
        it's more than the threshold we will accept that there is word at that position.

        returns (xpos_Array,ypos_Array) for each element in the table that is in the right format
        """
        masked_table = table.map(partial(self.isInTableElement,threshold=threshold,targetWord=targetWord)).to_numpy()

        return masked_table.nonzero()


    def findtable(self,table_list:list[table_format],targetWord:str,threshold:float) -> list[tuple[int,pd.DataFrame]]:
        """
        TODO find the wnt tables.
        return a list of wnt tables coupled to their year if available
        """
 
        table_list = tableAnalyser.tableListToDataFrameList(table_list)    
        

        for table in table_list:
            self.findInTable(table,targetWord,threshold)
            

    @staticmethod
    def tableListToDataFrameList(table_list:list[table_format]) -> list[pd.DataFrame]:
        """
        turns a list of table format into a list of dataframes
        """
        return [table.table() for table in table_list]


    @staticmethod
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
    analyser = tableAnalyser()

    for path in analyser.pathIterator():
        current_filename =path.split("/")[-1]
        if(current_filename in table_page_numbers.keys()):
            table_list = extractor(path).extract_gridbased(page_nums=table_page_numbers[current_filename])

            print(analyser.findtable(table_list,"gegevens",0.6))
            
