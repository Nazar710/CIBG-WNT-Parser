import os 
import pandas as pd 
from gridbased import table_extractor
from tqdm import tqdm 


"""
builds file structure and moves all files from the unsorted root folder (and all of it's subfolders)
to the sorted struct given information from WNT_labels.xlsx and File_labels.xlsx 
"""


if __name__ == "__main__": 
    to_be_sorted_root_folder_name = "unsorted" #make sure this root folder is in the same folder as sort_data.py


    ###########
    excel_wnt_labels = pd.read_excel("WNT_labels.xlsx") 
    excel_file_labels = pd.read_excel("File_labels.xlsx")

    nothingFound = set(excel_file_labels[excel_file_labels["WNTtype"]==0]["filename"])
    gridbased = set(excel_file_labels[excel_file_labels["WNTtype"]==1]["filename"])
    whitespace = set(excel_file_labels[excel_file_labels["WNTtype"]==2]["filename"])
    freetext = set(excel_file_labels[excel_file_labels["WNTtype"]==3]["filename"])

    scanned = set(excel_file_labels[excel_file_labels["Scanned"]==1]["filename"])

    #build folder struct
    if(not os.path.exists("sorted")):
        os.mkdir("sorted")

    for folder_name in ["gridbased","whitespace","freetext","nothing"]:
    
        if(not os.path.exists(os.path.join("sorted",folder_name))):
            os.mkdir(os.path.join("sorted",folder_name))
        
        for scanned_type in ["scanned","not_scanned"]:
            if(not os.path.exists(os.path.join("sorted",folder_name,scanned_type))):
                os.mkdir(os.path.join("sorted",folder_name,scanned_type))

    

    for path,file_name in tqdm(table_extractor.recursiveFilePathIterator(to_be_sorted_root_folder_name),ascii=True):
        target_path = os.path.join(os.curdir,"sorted")
        

        if(file_name in nothingFound):
            target_path = os.path.join(target_path,"nothing") 

        elif(file_name in gridbased):
            target_path = os.path.join(target_path,"gridbased") 

        elif(file_name in whitespace):
            target_path = os.path.join(target_path,"whitespace")

        elif(file_name in freetext):
            target_path = os.path.join(target_path,"freetext")

        else:
            print("FILE IS OF UNKNOWN TYPE",path)
            continue

        if(file_name in scanned):
            # scanned
            target_path = os.path.join(target_path,"scanned") 
        else:
            # not scanned
            target_path = os.path.join(target_path,"not_scanned")
        
        full_target_path = os.path.join(target_path,file_name)

        os.rename(path,full_target_path)