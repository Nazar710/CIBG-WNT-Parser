import pypdfium2 as pdfium
from tqdm import tqdm 


class candidates():
    def __init__(self,keywords:list=["bezoldiging", "wnt"]) -> None:
        self.keywords = keywords
    
    def get_candidates(self,pdf_path:str,hide_progress_bar:bool=False) -> list[int]:
        pdf = pdfium.PdfDocument(pdf_path) 
        candidate_pages = []


        for page_num,page in tqdm(enumerate(pdf),ascii=True,desc="find_candidate_pages",disable=hide_progress_bar):
            # Load a text page helper
            textpage = page.get_textpage()

            # Extract text from the whole page 
            text = textpage.get_text_range()
            
            if(self.isCandidate(text)):
                candidate_pages.append(page_num)

        return candidate_pages
    
    def needsOCR(self,pdf_path:str,hide_progress_bar:bool=False) -> list[int]:
        pdf = pdfium.PdfDocument(pdf_path)

        ocrNEEDEDPAGES = []
        for page_num,page in tqdm(enumerate(pdf),ascii=True,desc="find_OCR_required_pages",disable=hide_progress_bar):
            # Load a text page helper
            textpage = page.get_textpage()

            # Extract text from the whole page 
            text = textpage.get_text_range()
            
            if(len(text) ==0):
                ocrNEEDEDPAGES.append(page_num)
        return ocrNEEDEDPAGES

    def isCandidate(self,page:str) -> bool:
        text = page.lower()
        return all(keyword.lower() in text for keyword in self.keywords)


