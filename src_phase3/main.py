import os 
from typing import Generator
from thefuzz import fuzz
from functools import partial 
import numpy as np 
import pandas as pd  
import pdfplumber 


class extractor():
    def __init__(self) -> None:
        pass 

    def extract_table(self,path:str,page_nums:list[int]=None) -> tuple[list[pd.DataFrame],list[int]]:
        """
        extracts tables at the corresponding page or all tables from the entire document if no page numbers are provided. (so if page_nums = None)
        returns 2 lists, 1 with the tables and 1 with the page number for each table
        """
        with pdfplumber.open(path) as file:
            if(page_nums is not None):
                print("path: " + path)
                print("pages ", page_nums)
                table_pagenum_list= [(pd.DataFrame(table.extract()),page_num) for page_num in page_nums for table in file.pages[page_num].find_tables(table_settings=self.table_settings)] 
            else:
                table_pagenum_list= [(pd.DataFrame(table.extract()),page.page_number) for page in file.pages for table in page.find_tables(table_settings=self.table_settings)]
            
            tables = [table_and_page[0] for table_and_page in table_pagenum_list]
            page_nums = [table_and_page[1] for table_and_page in table_pagenum_list]
            return tables,page_nums    

    @staticmethod
    def extract(folder_name:str="example_pdfs",accepted_formats:list[str]=["pdf"]):
        """
        goes over all the pdfs in the specified folder and returns pdf objects
        
        """

    @staticmethod 
    def recursiveFilePathIterator(folder_name:str="example_pdfs",accepted_formats:list[str]=["pdf"]) -> Generator:
        """
        will grab any file that is of the accepted format within the entire file tree assuming provided folder name in the 
        current work directory to be root path.
        """
        root_path = os.path.join(os.curdir,folder_name)

        def recursiveIterator(current_folder_path:str):        
            for folder_elem in os.listdir(current_folder_path): 

                current_path = os.path.join(current_folder_path,folder_elem)

                if(os.path.isdir(current_path)):
                    #get data from folders
                    for path,file_name in recursiveIterator(current_path):
                        yield path,file_name
                else:
                    #get 
                    if(folder_elem.split(".")[-1] in accepted_formats):
                        yield current_path,folder_elem

        if(os.path.isdir(root_path)):
            for path,file_name in recursiveIterator(root_path):
                yield path,file_name
        else:
            yield None, None


class a1checker():
    def __init__(self) -> None:
        self.column_names = [
        "Naam",
        "Functiegegevens",
        "Aanvang en einde functievervulling in 2023",
        "Omvang dienstverband (als deeltijdfactor in fte)",
        "Dienstbetrekking",
        "Beloning plus belastbare onkostenvergoedingen",
        "Beloningen betaalbaar op termijn",
        "Subtotaal",
        "Individueel toepasselijke bezoldigingsmaximum",
        "-/- Onverschuldigd betaald en nog niet terugontvangen bedrag",
        "Bezoldiging",
        "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan",
        "Toelichting op de vordering wegens onverschuldigde betaling"
        ]
    
    
    def fuzzyElemMatching(self,table_elem:str,targetWord:str,threshold:float) -> bool:
        """
        treshold is between [0,1]
        checks if a word is close enough to a target word given some treshold measured.
        using fuzzy ratio matching
        """

        if(table_elem is None):
            return False 

        table_elem = table_elem.lower()
        targetWord = targetWord.lower()

        if(fuzz.ratio(table_elem,targetWord)/100 >= threshold): #/100 since fuzz ratio gives a number between [0,100]
            return True
        return False
    
    def findFuzzyMatchInTable(self,table:pd.DataFrame,targetWord:str,threshold:float) -> list[np.array]: #returns [pos ,pos pos] with pos being np.array([x,y])
        """
        threshold is from [0,1]
        Use fuzzy matching to see how similar the words are.
        it's more than the threshold we will accept that there is word at that position.

        returns [np.array[x,y],np.array[x,y]] for each element in the table that is in the right format
        """

        masked_table = table.map(partial(self.fuzzyElemMatching,threshold=threshold,targetWord=targetWord)).to_numpy()
        x,y = masked_table.nonzero()
        positions = np.concatenate((np.expand_dims(x,axis=1),np.expand_dims(y,axis=1)),axis=1)
        
        return [pos for pos in positions]

if __name__ == "__main__":

    extractObj = extractor() 
    extractObj.recursiveFilePathIterator()