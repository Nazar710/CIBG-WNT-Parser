import pypdfium2 as pdfium
from tqdm import tqdm 
from ocr_main import OCRMain


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
            text = textpage.get_text_range().lower()
            if(len(text) > 0):
                hasText = True
            
            if(all(keyword.lower() in text for keyword in self.keywords)):
                candidate_pages.append(page_num)

        #use OCR if no text
        if(not hasText):
            pages = OCRMain.on_file(pdf_path)
            for page_num,page in enumerate(pages):
                
                text = page.lower()
                if(all(keyword.lower() in text for keyword in self.keywords)):
                    candidate_pages.append(page_num)

        return candidate_pages


if __name__ == "__main__":
    can = candidates() 
    wnt_candidates = can.get_candidates("./wnt_not_scanned.pdf") 
    wnt_candidates = can.get_candidates("./wnt_scan.pdf") 

