from gridbased import table_analyser
from gridbased import table_extractor
import pandas as pd
from tqdm import tqdm
from typing import Any

class Evaluator():
    def __init__(self,) -> None:
        pass
    
    def evalgrid(self, download_spacy: bool,folder_name:str,gridtable_settings:dict={},**kwargs):
        #import gridbased functions
        self.table_extractor =  table_extractor(table_settings=gridtable_settings)
        self.table_analyser = table_analyser(download_spacy)
        extractor = table_extractor()
        
        #dataframe that grid based will fill in
        full_wntInfoTable = pd.DataFrame({"name":[],"bezoldiging":[],"year":[],"page":[],"file":[]}) 
         
        #results from our labeling
        WNT_labels = pd.read_excel("WNT_labels.xlsx")
        
        
        #iterate over each file and get the results from the grid based method
        for path,file_name in tqdm(self.table_extractor.recursiveFilePathIterator(folder_name,**kwargs),ascii=True):
            #pages from the labeling to feed to the grid based method
            wnt_pages = WNT_labels.loc[WNT_labels['FileName'] == file_name, 'Pagenumber'].unique()
            #convert to int
            wnt_pages = [(int(i)-1) for i in wnt_pages]
            
            #gridbased extraction
            extracted_tables, pages = self.table_extractor.extract_table(path,page_nums=wnt_pages)
            wntInfoTable = self.table_analyser.extractWNTInfo(extracted_tables,pages,file_name)
            full_wntInfoTable = pd.concat((full_wntInfoTable,wntInfoTable),ignore_index=True)
        return full_wntInfoTable
    
    def eval_names(self, labeled_data, data_found):
        
        relevant_names_retrieved = 0
        retrieved_names = 0
        relevant_names = 0
        
        for file_name in labeled_data["FileName"].unique():
            target_names = labeled_data.loc[labeled_data['FileName'] == file_name]["Name"].tolist()
            retrieved = data_found.loc[data_found["file"]==file_name]["name"].tolist()
            
            relevant_names = relevant_names + len(target_names)
            retrieved_names = retrieved_names + len(retrieved)
            
            for name in retrieved:
                for target in target_names:
                    if(name == target):
                        relevant_names_retrieved = relevant_names_retrieved+1
                        target_names.remove(target)
        precision = relevant_names_retrieved/retrieved_names
        recall = relevant_names_retrieved/relevant_names
        print("precision: ", precision)
        print("recall", recall)
                    
if __name__ == "__main__":
    #general settings 
    eval= Evaluator()
    # print(pd.read_excel("WNT_labels.xlsx").head)
    # print(pd.read_csv("resultsgrid.csv")["file"])
    eval.eval_names(pd.read_excel("WNT_labels.xlsx"),pd.read_csv("resultsgrid.csv"))
    
    
    
