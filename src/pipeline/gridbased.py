import pdfplumber 
import pandas as pd 
import os 
from typing import Generator
import pandas as pd 
from functools import partial
import numpy as np 
from thefuzz import fuzz
import spacy



class table_extractor():
    """
    extractor for gridbased and free text
    """
    def __init__(self,table_settings:dict={}) -> None:
        self.table_settings = table_settings

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
    def filePathIterator(directory_files:str="example_pdfs",accepted_formats:list[str]=["pdf"]) -> Generator:
        """
        returns an iterator for all the file paths to a directory and the file name
        """
        root_path = os.path.join(os.curdir,directory_files)
        for file_path in os.listdir(root_path):
            if(file_path.split(".")[-1] in accepted_formats):
                yield os.path.join(root_path,file_path),file_path
    
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
            



class table_analyser():
    def __init__(self,download_spacy:bool=False) -> None:
        
        if(download_spacy):
            spacy.cli.download("nl_core_news_sm")

        self.NER = spacy.load("nl_core_news_sm")

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
    
    def elemEntityMatching(self,table_elem:str,targetEntity:str) -> bool:
        """
        finds matches for entities
        some targetEntities that work: 
        DATA,CARDINAL,ORG,PERSON,EVENT,FAC,WORK_OF_ART,NORP,GPE,LOC
        """
        if(table_elem is None):
            table_elem = ""

        _,_,entities = self.entity_replacer(table_elem)

        return targetEntity in entities


    def entity_replacer(self,text:str) -> tuple[str,str,list[str]]:
        """
        replaces all the words in the text with their found entity type.

        return orignal string, the string with all it's enities replaced by their entity type

        lower to reduce the risk of miss binding of entities.
          
                gegevens 2020 -> gegevens [date].  
                Gegevens 2020 -> [data]
        but person names will not work be seen as persons when you lower the capitalization of the letters.
        so first without lowering extract the [persons] locations, afterwards rerun with lower and extract the other named entity locations
        Then replace the named entities with [NAMED ENTITY TYPE]
        """
        ents = self.NER(text).ents  

        mask = np.ones(len(text))
        labels = []

        found_entities = []

        #detect persons 
        for ent in ents:
            if(ent.label_ == "PERSON"):
                mask[ent.start_char:ent.end_char] = 0
                labels.append((ent.start_char,ent.label_))
                found_entities.append(ent.label_)
    
        text = text.lower()
        #detect the rest
        for ent in ents:
            mask[ent.start_char:ent.end_char] = 0
            labels.append((ent.start_char,ent.label_))   
            found_entities.append(ent.label_)       

        labels = [elem[1] for elem in sorted(labels,key=lambda elem: elem[0])] 

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

        return text,new_text,found_entities
    

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
    
    def findEntityInTable(self,table:pd.DataFrame,targetEntity:str) -> list[np.array]:
        """
        find the positions of a specific entity in a table 
        """
        masked_table = table.map(partial(self.elemEntityMatching,targetEntity=targetEntity)).to_numpy()
        x,y = masked_table.nonzero()
        positions = np.concatenate((np.expand_dims(x,axis=1),np.expand_dims(y,axis=1)),axis=1)
        
        return [pos for pos in positions] 

    def gegevens_refinement(self,table:pd.DataFrame,positions:list[np.array]) -> tuple[list[np.array],list[int]]:
        """
        only return gegevens with date, odities should be pruned away
        returns positions, years
        """

        years = []
        final_positions = []

        for pos in positions:
            x,y = pos
            elem = table.iloc[x][y]
            year = elem.split(" ")[-1]
            try:
                years.append(int(year))
                final_positions.append(pos)

            except:
                print("gegevens not followed by a number: ",elem)
                pass 
        
        return final_positions,years
    
    def bezoldiging_refinement(self,table:pd.DataFrame,positions:list[np.array]) -> list[np.array]:
        """
        only return bezoldigings, any odities should be pruned away.
        returns positions 

        """ 
        updated_positions = []
        
        for pos in positions:
            x,y = pos 
            elem = table.iloc[x,y]
            
            #reject when contains maximum
            if(not "maximum" in elem):
                updated_positions.append(pos)
            
        return updated_positions
    
    def person_refinement(self,table:pd.DataFrame,positions:list[np.array]) -> list[np.array]:
        """
        only return personnames, any odities should be pruned away.
        returns positions excluding the ones that were pruned away
        """
        not_a_name = ["kalenderjaar","directeur"]
        new_positions = []
        for pos in positions:
            x,y = pos 
            elem = table.iloc[x,y]
            
            if(not (elem.lower() in not_a_name)):
                #not a name
                new_positions.append(pos)

        return new_positions


    def bezoldiging_value_extraction(self,table:pd.DataFrame,position_bezoldiging_label:np.array,person_positions:list[np.array]) -> list[tuple[str,float]]:
        """
        using the position of the bezoldiging_label, it will couple the subsequent values to the person names.
        returns a dictionary of names coupled with values
        """
        person_bezoldiging = []

        for person_pos in person_positions:
            x_person,y_person = person_pos #x is rows, y is columns
            x_bezoldiging_label,_ = position_bezoldiging_label
            
            if(x_person < x_bezoldiging_label):
                name = table.iloc[x_person,y_person]
                # print("name: ",name)
                bezoldiging = table.iloc[x_bezoldiging_label,y_person]
                # print("bezoldiging: ", bezoldiging)
                person_bezoldiging.append((name,bezoldiging))
        return person_bezoldiging
            


    def extractWNTInfo(self,wnt_tables:list[pd.DataFrame],page_num:list[int],file_name:str) -> pd.DataFrame:
        """
        extract the (year,person_name,totale bezoldiging,page) for each person in the wnt table
        return a table with this
        """
        final_dataframe = pd.DataFrame({"name":[],"bezoldiging":[],"year":[],"page":[],"file":[]})
        
        for table,page_num in zip(wnt_tables,page_num):
            #find table year and the position 
            gegevens_positions = self.findFuzzyMatchInTable(table,"gegevens",0.75)
            
            gegevens_positions,years = self.gegevens_refinement(table,gegevens_positions)#refinement

            #find person positions
            person_positions = self.findEntityInTable(table,"PERSON")
            
            person_positions = self.person_refinement(table,person_positions)#refinment

            #find bezoldiging row 
            bezoldiging_positions = self.findFuzzyMatchInTable(table,"bezoldiging",0.8)
            bezoldiging_positions += self.findFuzzyMatchInTable(table,"totaal bezoldiging",0.8)

            bezoldiging_positions = self.bezoldiging_refinement(table,bezoldiging_positions)#refinement

            #build table 
            #first tag the positions (pos,label,*extra_info)
            couple_gegevens_positions = [(pos,"year",years[index]) for index,pos in enumerate(gegevens_positions)] #tag the positions
            coupled_bezoldinging_positions = [(pos,"bezoldiging") for pos in bezoldiging_positions] #tag the bezoldiging positions
            coupled_positions = couple_gegevens_positions + coupled_bezoldinging_positions 
            #sort on the x-axis
            coupled_positions = sorted(coupled_positions,key=lambda elem: elem[0][0]) 

            #algorithm
            current_year = None 
            final_tuples = []

            for pos,label,*info in coupled_positions:
                if(label == "year"):
                    current_year = info[0] 

                elif(label == "bezoldiging"):
                    #since it only gives the row not the elements first extract the elements
                    bezoldiging_values_with_person = self.bezoldiging_value_extraction(table,pos,person_positions)
                    #add year to tuple 
                    final_tuples = [pd.DataFrame({"name":[name],"bezoldiging":[bezoldiging],"year":[str(current_year)],"page":[str(page_num)],"file":[file_name]}) for name,bezoldiging in bezoldiging_values_with_person]

                    #store tuples in table

                    for df in final_tuples:
                        final_dataframe = pd.concat((final_dataframe,df),ignore_index=True)

                    #reset year
                    current_year = None 
        return final_dataframe