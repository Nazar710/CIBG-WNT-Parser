import pandas as pd
import datetime
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
        confirmed_data = []
        
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
                    potential_data = [] # a temporary list that contains the data points.
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
                        confirmed_data.append(datapoint)
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
            A tuple containing two things:
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
            A tuple containing three things:
            - in its first position, a boolean that is true if the method found a name and false if it did not
            - in its second position, a list that contains the names. If nothing got found, None
            - in its third position,the location of the last character of the last name in the string. If nothing got found, None
            - in its fourth position, the label for the type of data this tuple contains. In this case 2
        
        """
        #TODO: implement this method
        if(start_character < 2):
            return (True, ["Mathias"], 2,2)
        if(start_character < 4):
            return (True, ["Mattie"], 4,2)
        else: return (False, None, None,2)
    @staticmethod
    def find_bezoldiging(text:str, start_character:int)->(bool,str,int,int): 
        """ 
        given the string, this method uses rules to find the values for bezoldiging that appear
        after the starting character.
        
        Args:
            text: the text for the method to search
            start_character: the character from which the search should start
        
        Returns:
            A tuple containing three things:
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

if __name__ == "__main__":
    list = extract_free_text.extract("123456789123456789",2020,12,"je_moeder.txt")
    print(list)