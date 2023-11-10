import pdfplumber 
import pandas as pd 
import matplotlib.pyplot as plt 
import Levenshtein
import thefuzz
import os 
from typing import Generator
import pandas as pd 



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


def findtable(table_list:list[table_format]):
    pass 


def pathIterator(directory_files:str="example_pdfs",accepted_formats:list[str]=["pdf"]) -> Generator:
    """
    returns an iterator for all the file paths to a directory
    """
    root_path = os.path.join(os.curdir,directory_files)
    for file_path in os.listdir(root_path):
        if(file_path.split(".")[-1] in accepted_formats):
            yield os.path.join(root_path,file_path)


if __name__ == "__main__":
    itr = pathIterator()

    extr = extractor("./example_pdfs/wnt_grid.pdf") 
