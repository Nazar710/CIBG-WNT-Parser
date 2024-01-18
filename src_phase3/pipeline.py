import a1checker.a1checkerMain as a1checkerMain 
import a1checker.pdfWrapper as pdfWrapper
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



def whiteSpace(pdf_path:str,pagenumber:int,wrappedPDF:pdfWrapper) -> None:
    #whitespace tables

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
        wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=len(tables) > 0,csv_path="",csv_method="white space",tables=tables)


def pipeline(pdf_path_list:list[str], folder_path: str):
    #hyper param
    treshold = 0.7 
    keywords = ["bezoldiging", "wnt"]
    minNumRowsMatched = 10
    tesseract_cmd_path = r'D:/CODING/Tesseract-OCR/tesseract.exe'
    hidden_progress_bar = True
        
    Extractor = a1checkerMain.extractor()
    checker = a1checkerMain.a1checker()

    wrappedPdfs =[checker.is1aOrNot(pdfobj,treshold,minNumRowsMatched) for pdfobj in Extractor.extractFromPathList(pdf_path_list)]

    for wrappedPDF in wrappedPdfs:
        pdf_path = wrappedPDF.file_path
        candidate_finder = speedy_candidates.candidates(keywords)
        #candidate pages 
        candidate_pages = candidate_finder.get_candidates(pdf_path,hide_progress_bar=hidden_progress_bar)

        for pagenumber in candidate_pages:     
            #exact match 
            exact_match_table,isExactMatch = exactmatch_whitespace.extract_data_from_pdf(pdf_path,pagenumber,minNumRowsMatched)
            
            if(isExactMatch):
                wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=True,csv_path="",csv_method="exact white space",tables=exact_match_table)
            else: #not exact match 
                whiteSpace(pdf_path,pagenumber,wrappedPDF)

        if(not wrappedPDF.has1ATable):
            
            for pagenum in tqdm(candidate_finder.needsOCR(pdf_path,hidden_progress_bar),ascii=True,desc="OCR"):
                # Create an instance of SearchablePDFConverter
                pdf_converter = scannedConvert.SearchablePDFConverter(pdf_path, tesseract_cmd_path)

                # Example 2: Convert a specific page of the PDF to a searchable PDF with post-processing
                searchable_pdf_page = pdf_converter.convert_to_searchable_pdf_page(pagenum)

                # Save the output searchable PDF for the specific page to a file
                searchable_pdf_page_output_path = f'tempSearchable.pdf'
                searchable_pdf_page.save(searchable_pdf_page_output_path)
                whiteSpace("tempSearchable.pdf",pagenum,wrappedPDF)
                
    for pdf in tqdm(wrappedPdfs):
        for page in pdf.pages:
            if page.has_1a_table:
                if type(page._tables) is list:
                    for tablenum, table in enumerate(page._tables):
                        csv_path = os.path.join(folder_path, pdf.file_name[:-4]+str(page.page_number+tablenum)+".csv")
                        table.to_csv(csv_path)
                        page.csv_path = csv_path
                else:
                    csv_path = os.path.join(folder_path, str(pdf.file_name[:-4] + str(page.page_number)+".csv"))
                    page.csv_path = csv_path
                    page._tables.to_csv(csv_path)
    debug_gui = debugger.PDFViewer(wrappedPdfs)
    debug_gui.run()
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFProcessorApp(root,pipeline)
    root.mainloop()