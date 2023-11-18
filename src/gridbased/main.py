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
import spacy

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
    def __init__(self,matching_func:Callable=fuzz.ratio,entityTypeReplacement:bool=True,download_spacy:bool=False) -> None:
        self.matching_func = matching_func
        self.entityTypeReplacement = entityTypeReplacement #maps entities in text comparisons to their entity type instead of their value. (so you can compare groups instead of being overfocust on individual instanced of an entity goup)

        if(download_spacy):
            spacy.cli.download("nl_core_news_sm")

        self.NER = spacy.load("nl_core_news_sm")


    def isInTableElement(self,table_elem:str,targetWord:str,threshold:float) -> bool:
        """
        checks if a word is close enough to a target word given some treshold measured.
        Where the distance is measured by an by the instance provided matching function. (self.matching_fun)
        """

        if(table_elem is None):
            return False 

        #first lower to reduce the risk of miss binding of entities.
        #since:  
        #        gegevens 2020 -> gegevens [date].  
        #        Gegevens 2020 -> [data]

        table_elem = table_elem.lower()
        targetWord = targetWord.lower()

        if(self.entityTypeReplacement):
            #TODO since there is a distinction made between CARDINALITY and MONEY labels (and similar instances) it might be necisary to find groups of entities labels and map them to the same thing

            table_elem = self.entity_replacer(table_elem)[1]
            targetWord = self.entity_replacer(targetWord)[1]

        if(self.matching_func(table_elem,targetWord) >= threshold):
            return True
        return False

    def findInTable(self,table:pd.DataFrame,targetWord:str,threshold:float,acceptable_x:list=None,acceptable_y:list=None) -> list[np.array]: #returns [pos ,pos pos] with pos being np.array([x,y])
        """
        Use fuzzy matching to see how similar the words are.
        
        fuzzy matching has a value in range [0,100].
        it's more than the threshold we will accept that there is word at that position.

        acceptable_x and acceptable_y are used to define what row and column are accepted.

        returns [np.array[x,y],np.array[x,y]] for each element in the table that is in the right format
        """

        masked_table = table.map(partial(self.isInTableElement,threshold=threshold,targetWord=targetWord)).to_numpy()
        x,y = masked_table.nonzero()
        positions = np.concatenate((np.expand_dims(x,axis=1),np.expand_dims(y,axis=1)),axis=1)
        
        return [pos for pos in positions if (acceptable_x is None or pos[0] in acceptable_x) and  (acceptable_y is None or pos[1] in acceptable_y)]


    def entity_replacer(self,text:str) -> tuple[str,str]:
        """
        replaces all the words in the text with their found entity type.

        return orignal string, the string with all it's enities replaced by their entity type
        """
        ents = self.NER(text).ents  

        mask = np.ones(len(text))
        labels = []
        for ent in ents:
            mask[ent.start_char:ent.end_char] = 0
            labels.append(ent.label_)

        current_num = 1 
        current_label_index = 0
        new_text = ""
        for text_pos,num in enumerate(mask):
            if(num < current_num):
                new_text += "["+labels[current_label_index]+"]"
                current_label_index += 1
            
            if(num == 1):
                new_text += text[text_pos]
            current_num = num 

        return text,new_text


    def findtable(self,table_list:list[table_format],threshold:float) -> list[tuple[int,pd.DataFrame]]:
        """
        TODO find the wnt tables.
        return a list of wnt tables coupled to their year if available
        """
 
        table_list = tableAnalyser.tableListToDataFrameList(table_list)    


        for table in table_list:


            print(self.findInTable(table,"bezoldiging",threshold,acceptable_x=[0,1],acceptable_y=[0,1]))

    def extractWntTable(wnt:pd.DataFrame):
        """
        TODO get the information out of the found wnt table into a nice standardized representation 
        """
        pass        

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


"""
first find what is a wnt table and if possible give it's corresponding year:
    -
    -
    -
after this extract the wnt table.

"""



if __name__ == "__main__":
    #param 
    download_spacy = False 

    #wnt extraction test
    table_page_numbers = {"wnt_grid.pdf":[39,40],"wnt_grid2.pdf":[35,36]}    
    analyser = tableAnalyser(download_spacy=download_spacy)

    for path in analyser.pathIterator():
        current_filename =path.split("/")[-1]
        if(current_filename in table_page_numbers.keys()):
            table_list = extractor(path).extract_gridbased(page_nums=table_page_numbers[current_filename])

            print(analyser.findtable(table_list,0))