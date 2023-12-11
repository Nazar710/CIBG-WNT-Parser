import pypdfium2 as pdfium
from tqdm import tqdm 
from ocr_main import OCRMain
from gridbased import table_extractor
import pandas as pd 
from time import time


class candidates():
    def __init__(self,keywords:list=["bezoldiging", "wnt"]) -> None:
        self.keywords = keywords
    
    def get_candidates(self,pdf_path:str) -> list[int]:
        pdf = pdfium.PdfDocument(pdf_path) 
        candidate_pages = []

        hasText = False

        for page_num,page in tqdm(enumerate(pdf),ascii=True,desc="find_candidate_pages"):
            # Load a text page helper
            textpage = page.get_textpage()

            # Extract text from the whole page 
            text = textpage.get_text_range()
            if(len(text) > 0):
                hasText = True
            
            if(self.isCandidate(text)):
                candidate_pages.append(page_num)

        #use OCR if no text
        if(not hasText):
            pages = OCRMain.on_file(pdf_path)
            for page_num,page in enumerate(pages):
                
                if(self.isCandidate(page)):
                    candidate_pages.append(page_num)

        return candidate_pages

    def isCandidate(self,page:str) -> bool:
        text = page.lower()
        return all(keyword.lower() in text for keyword in self.keywords)



if __name__ == "__main__":
    can = candidates() 
    # wnt_candidates = can.get_candidates("./wnt_not_scanned.pdf") 
    # print(wnt_candidates)
    # wnt_candidates = can.get_candidates("./wnt_scan.pdf") 
    # print(wnt_candidates)
    df = pd.DataFrame({"filename":[],"results":[]})
    t0 = time()
    
    for path,file_name in table_extractor.recursiveFilePathIterator("./allPDF_1"):
        
        df_row = pd.DataFrame({"filename":[file_name],"results":[can.get_candidates(path)]})
        
        df = pd.concat([df,df_row],ignore_index=True)
    t1 = time() - t0
    print(t1)
    df.to_csv("speedy_candidates_results.csv")