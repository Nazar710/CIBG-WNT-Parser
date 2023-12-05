import pandas as pd
import datetime
import re
import spacy
class extract_free_text:
    @staticmethod
    def extract(text:str,page:int,file:str,default_year:int = None):
        """ 
        this method applies an algorithm that parses through the input text and creates triples of
        data points that contain the extracted information.
        
        TODO: implement a check that removes the last few data points and throws an error
        if the amount of bezoldigingen found did not match the amount of names found.
        
        Args:
            text: the text for the method to search
            default_year: the year that the document should default to. None by default
            page: page number that the text came from
            file: file that the text came from
        
        Returns:
            A list of triples that each contain a datapoint.
        
        """
        character = 0 # the character where our search is at. start at 0
        current_year = default_year # the year we currently have recorded
        names_list = [] # the names we have found so far
        current_name = None
        data_left = True
        confirmed_data = [] # data that did not contradict anything
        potential_data = [] # a temporary list that contains the datalist before they are checked
        while(character<len(text) and data_left):
            
            # try to find the next instances of a year, names and bezoldiging
            next_year = extract_free_text.find_year(text,character)
            next_names = extract_free_text.find_names(text, character)
            next_bezoldiging = extract_free_text.find_bezoldiging(text, character)
            
            #if they exist, place them in a list of potential next data points
            next_datapoints = []
            if next_year[0]: next_datapoints.append(next_year)
            if next_names[0]: next_datapoints.append(next_names)
            if next_bezoldiging[0]: next_datapoints.append(next_bezoldiging)
            else: 
                data_left = False #if there is no bezoldiging left in the text, exit the loop
                
                #add the potential data points to the confirmed datapoint if it matches up with the number of names
                if (len(potential_data)%len(names_list)==0):
                        confirmed_data.append(potential_data)
                continue
            
            #find the first datapoint could be found, the one with the lowest value for its character
            next = min(next_datapoints, key = lambda t: t[2])
            
            #now, handle the different cases for the different types of datapoints that were found
            match next[3]:
                
                # the next datapoint is a year
                case 1:
                    # set the current year to what you found
                    current_year = next[1]
                    
                # the next datapoint is a name or names
                case 2:
                #add the potential data points to the confirmed datapoint if it matches up with the number of names
                    if (len(names_list)!= 0) and (len(potential_data)%len(names_list)==0):
                        confirmed_data.append(potential_data)
                        
                    names_list = next[1]
                    current_name = 0
                    # you encountered a name, reset to the default year
                    current_year = default_year
                    
                # the next datapoint is a bezoldiging
                case 3:
                    if(current_name is not None):
                        # if you have encountered a name before, create a data point with the bezoldiging, the name 
                        # and the current year.
                        datapoint = (str(names_list[current_name]),str(next[1]),str(current_year),str(page),str(file))
                        potential_data.append(datapoint)
                        #if your method found multiple names, move to the next
                        if current_name < len(names_list)-1:
                            current_name = current_name+1
            character = next[2] # let the next iteration of the loop start where the last datapoint ended.
            
        df = pd.DataFrame(confirmed_data, columns=["name", "bezoldiging", "year", "page", "file"]) 
        return df
                                      
    @staticmethod
    def find_year(text:str, start_character:int)->(bool,int,int,int): 
        """ 
        given the string, this method uses rules to find the first instance of a year that appears after the
        starting character. Key words to look for are "gegevens" 
        
        Args:
            text: the text for the method to search
            start_character: the character from which the search should start
        
        Returns:
            A tuple containing four things:
            - in its first position, a boolean that is true if the method found a year and false if it did not
            - in its second position, the year it found. If nothing got found, None
            - in its third position, the location of the last character of the year in the string. If nothing got found, None
            - in its fourth position, the label for the type of data this tuple contains. In this case 1
        
        """
        #TODO: implement this method
        if(start_character < 1):
            return (True, 2020, 1,1)
        if(start_character<5) :
            return (True, 2019, 5,1)
        else: return (False, None, None,1)
    @staticmethod
    def find_names(text:str, start_character:int)->(bool,list[str],int,int): 
        """ 
        given the string, this method uses rules and NER to find the first instance of names that appears 
        after the starting character. If names appear right after eachother, this method should return a list of 
        all those names.
        
        Args:
            text: the text for the method to search
            start_character: the character from which the search should start
        
        Returns:
            A tuple containing four things:
            - in its first position, a boolean that is true if the method found a name and false if it did not
            - in its second position, a list that contains the names. If nothing got found, None
            - in its third position,the location of the last character of the last name in the string. If nothing got found, None
            - in its fourth position, the label for the type of data this tuple contains. In this case 2
        
        """
        #TODO: implement this method
        free_text_obj = FreeText(download_spacy=False)
        name,_,end = free_text_obj.find_named_entity_from_index(text,start_character)
        if(end == -1):
            return (False,None,None,2)
        else:
            return(True,name,end,2)
        
    @staticmethod
    def find_bezoldiging(text:str, start_character:int)->(bool,str,int,int): 
        """ 
        given the string, this method uses rules to find the values for bezoldiging that appear
        after the starting character.
        
        Args:
            text: the text for the method to search
            start_character: the character from which the search should start
        
        Returns:
            A tuple containing four things:
            - in its first position, a boolean that is true if the method found a name and false if it did not
            - in its second position, the value of the bezoldiging. If nothing got found, None
            - in its third position, the location of the last character of this string. If nothing got found, None
            - in its fourth position, the label for the type of data this tuple contains. In this case 3
        """
        #TODO: implement this method
        if(start_character < 3):
            return (True, ["15 an hour"], 3,3)
        if(start_character < 6):
            return (True, ["money"], 6,3)
        else:
            return (False, None, None,3)

#zijian's code
# if you didn't download spacy plz turn bool = True ⬇
class FreeText:
    def __init__(self, download_spacy: bool = False, nlp_core_path: str = "nl_core_news_sm") -> None:
        if download_spacy:
            spacy.cli.download(nlp_core_path)
        self.NER = spacy.load(nlp_core_path)

    def find_named_entity_from_index(self, text: str, start_index: int) -> tuple:
        """
        Find the first named entity in the text starting from the given index.
        :param text: The input text.
        :param start_index: The index to start searching for named entities.
        :return: A tuple containing the named entity, its starting index, and its ending index.
                 If no named entity is found, returns an empty string and -1 for both indices.
        """
        # Define a pattern for uppercase_dot with 1-4 repetitions
        pattern = re.compile(r'([A-Z]\.){1,4}')
        # Find all matches in the given text
        matches = pattern.findall(text[start_index:])
        ents = self.NER(text[start_index:]).ents

        # Convert matches to a common format
        matches_entities = [(match, start_index + text[start_index:].find(match),
                             start_index + text[start_index:].find(match) + len(match)) for match in matches]

        # Convert spaCy entities to a common format
        spacy_entities = [(entity.text, start_index + entity.start_char, start_index + entity.end_char)
                          for entity in ents if entity.label_ == 'PERSON']

        # Combine both sets of entities
        all_entities = matches_entities + spacy_entities
        all_entities = sorted(all_entities, key=lambda x: x[1])

        count = 0;
        entity_start_index = -1
        entity_end_index = -1
        text = ""
        for entity in all_entities:
            count += 1
            if count == 1:
                entity_start_index = entity[1]
                entity_end_index = entity[2]
                text = entity[0]
            if count == 2:
                interval = text[entity_end_index:entity[1]]
                if any(char.isalpha() for char in interval):
                    print("The 2 names:", text, entity[0], " are connected")

        return text, entity_start_index, entity_end_index

if __name__ == "__main__":
    # Example usage
    test_text = """P.A. Robin R.J. Mathias en Jade gaan uit eten
    01/01 - 31/12 """


    start_index = 0
    free_text_obj = FreeText(download_spacy=False)
    named_entity, entity_start_index, entity_end_index = free_text_obj.find_named_entity_from_index(test_text,
                                                                                                    start_index)
    print(named_entity, entity_start_index, entity_end_index)



