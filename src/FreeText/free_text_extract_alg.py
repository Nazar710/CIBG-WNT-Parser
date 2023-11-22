def extract(text:str, default_year:int):

    character = 0 # the character where our search is at. start at 0
    current_year = default_year # the year we currently have recorded
    names_list = [] # the names we have found so far
    current_name = None
    data_left = True
    
    while(character<len(text) and data_left):
        
        # try to find the next instances of a year, names and bezoldiging
        next_year = find_year(text,character)
        next_names = find_names(text, character)
        next_bezoldiging = find_bezoldiging(text, character)
        
        #if they exist, place them in a list of potential next data points
        next_datapoints = []
        if next_year[0]: next_datapoints.append(next_year)
        if next_names[0]: next_datapoints.append(next_names)
        if next_bezoldiging[0]: next_datapoints.append(next_bezoldiging)
        
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
                names_list = next[1]
                current_name = 0
                # you encountered a name, reset to the default year
                current_year = default_year
                
            # the next datapoint is a bezoldiging
            case 3:
                if(current_name is not None):
                    # if you have encountered a name before, create a data point with the bezoldiging, the name 
                    # and the current year.
                    datapoint = (current_year,names_list[current_name],next[1])
                    
                    #if your method found multiple names, move to the next
                    if current_name < len(names_list)-1:
                        current_name = current_name+1
                    
                        
                        
                        
                    
                

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
        - in its second position, the year it found
        - in its third position, the location of the last character of the year in the string
        - in its fourth position, the label for the type of data this tuple contains. In this case 1
    
    """
    #TODO: implement this method
    return (True, 0, start_character+1)

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
        - in its second position, a list that contains the names 
        - in its third position,the location of the last character of the last name in the string
        - in its fourth position, the label for the type of data this tuple contains. In this case 2
    
    """
    #TODO: implement this method
    return (True, [""], start_character+2)

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
        - in its second position, the value of the bezoldiging
        - in its third position, the location of the last character of this string
        - in its fourth position, the label for the type of data this tuple contains. In this case 3
    """
    #TODO: implement this method
    return (True, [""], start_character+3)

if __name__ == "__main__":
    lala = []
    lala.append(1)
    lala.append(2)
    lala.append(3)
    while(i<len(lala))