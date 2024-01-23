import a1checker.a1checkerMain as a1checkerMain 
import a1checker.pdfWrapper as pdfWrapper
import a1checker.better_match as better_match
import whiteSpace.nameFind as nameFind
import whiteSpace.whitespaceMain as whitespaceMain
import whiteSpace.scannedConvert as scannedConvert
import whiteSpace.exactmatch_whitespace as exactmatch_whitespace
import candidatepageFinder.speedy_candidates as speedy_candidates
from tqdm import tqdm
from visualDebug.visualMain import PDFProcessorApp
from tkinterdnd2 import DND_FILES, TkinterDnD
import visualDebug.pdfViewer as debugger
import os
import pytesseract



def whiteSpace(pdf_path:str,pagenumber:int,wrappedPDF:pdfWrapper,is_ocr:bool = False) -> None:
    #whitespace tables

    original_page = pagenumber
    if(is_ocr):
        pagenumber = 1
        csv_method = "OCR whitespace"
    else:
        csv_method = "whitespace"

    keyword_finder = nameFind.KeywordFinder(pdf_path)
    result = keyword_finder.find_keywords_with_context(pagenumber)
    keyword_finder.close()
    listofnames=result               
    pdf_processor = whitespaceMain.PDFProcessor()
    pdf_processor.process_pdf(pdf_path=pdf_path, target_page=pagenumber, names=listofnames)
   
    
    #page_number:int, selectable:bool, scanned:bool, has_1a_table:bool, csv_path:str,csv_method:str,tables:list[pd.DataFrame])
    tables = pdf_processor.return_results()
    
    if(len(tables) > 0):
        #only adds page if it's 1a
        wrappedPDF.add_page(page_number=original_page,selectable=True,scanned=False,has_1a_table=len(tables) > 0,csv_path="",csv_method=csv_method,tables=tables)
    

def pipeline(pdf_path_list:list[str], folder_path: str):
    #hyper param
    treshold = 0.9 
    keywords = ["bezoldiging", "wnt"]
    minNumRowsMatched = 10
    tesseract_cmd_path = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
    hidden_progress_bar = True
        
    Extractor = a1checkerMain.extractor()
    checker = a1checkerMain.a1checker()
    matcher = better_match.better_match()

    wrappedPdfs =[checker.is1aOrNot(pdfobj,treshold,minNumRowsMatched) for pdfobj in Extractor.extractFromPathList(pdf_path_list)]

    for wrappedPDF in wrappedPdfs:
        pdf_path = wrappedPDF.file_path
        candidate_finder = speedy_candidates.candidates(keywords)
        #candidate pages 
        candidate_pages = candidate_finder.get_candidates(pdf_path,hide_progress_bar=hidden_progress_bar)

        for pagenumber in candidate_pages:     
            #exact match 
            keyword_match_tables,exact_match_tables = matcher.get_tables(pdf_path=pdf_path,page_number=pagenumber)
            
            if len(exact_match_tables)>0:
                # get the largest table from the list of exact matching tables
                max_table = exact_match_tables[0]
                for table in exact_match_tables:
                    if table.size > max_table.size:
                        max_table = table
                wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=True,csv_path="",csv_method="exact matcher",tables=max_table)
            elif len(keyword_match_tables)>0:
                # get the largest table from the list of keyword matching tables
                max_table = keyword_match_tables[0]
                for table in keyword_match_tables:
                    if table.size > max_table.size:
                        max_table = table
                wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=True,csv_path="",csv_method="keyword matcher",tables=max_table)
            else: #not exact match 
                try:
                    whiteSpace(pdf_path,pagenumber,wrappedPDF)
                except:
                    pass

        if(not wrappedPDF.has1ATable()):
            
            for pagenum in tqdm(candidate_finder.needsOCR(pdf_path,hidden_progress_bar),ascii=True,desc="OCR"):
                # Create an instance of SearchablePDFConverter
                pdf_converter = scannedConvert.SearchablePDFConverter(pdf_path, tesseract_cmd_path)

                # Example 2: Convert a specific page of the PDF to a searchable PDF with post-processing
                searchable_pdf_page = pdf_converter.convert_to_searchable_pdf_page(pagenum)

                # Save the output searchable PDF for the specific page to a file
                searchable_pdf_page_output_path = f'tempSearchable.pdf'
                searchable_pdf_page.save(searchable_pdf_page_output_path)
                whiteSpace("tempSearchable.pdf",pagenum,wrappedPDF,is_ocr=True)
                
    for pdf in tqdm(wrappedPdfs):
        for page in pdf.pages:
            if page.has_1a_table:
                if type(page._tables) is list:
                    for tablenum, table in enumerate(page._tables):
                        csv_path = os.path.join(folder_path, pdf.file_name[:-4]+str(page.page_number)+"-"+str(tablenum)+page.csv_method+".csv")
                        if not (page.csv_method == "exact matcher" or page.csv_method == "keyword matcher"):
                            table.transpose().to_csv(csv_path)
                        else:
                            table.to_csv(csv_path)
                        page.csv_path = csv_path
                              
                else:
                    csv_path = os.path.join(folder_path, str(pdf.file_name[:-4] + str(page.page_number)+page.csv_method+".csv"))
                    page.csv_path = csv_path

                    if not (page.csv_method == "exact matcher" or page.csv_method == "keyword matcher"):
                        page._tables.transpose().to_csv(csv_path)## fix (table ->page._tables
                    else:
                        page._tables.to_csv(csv_path)## fix (table ->page._tables
                        
    debug_gui = debugger.PDFViewer(wrappedPdfs)
    debug_gui.run()
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFProcessorApp(root,pipeline)
    root.mainloop()