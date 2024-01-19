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
import sys
import pandas as pd 
import subprocess

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

class evaluator():
    def __init__(self,a1tablePagePhoneBook_path:str,output_folder_path:str,labelled_folder_path:str) -> None:    
        self.output_folder_path = output_folder_path
        self.labelled_folder_path = labelled_folder_path
        self.a1tablePagePhoneBook_path = a1tablePagePhoneBook_path

    def compare_to_all(self):
        """
        """

        total_phonebook = pd.read_excel(self.a1tablePagePhoneBook_path)
        A1_phonebook = total_phonebook[total_phonebook["1a present"] == 1]

        for path_label,labeled_file_name in a1checkerMain.extractor.recursiveFilePathIterator(self.labelled_folder_path,["xlsx"]):
            pdf_file_name =labeled_file_name[:-5]+".pdf"

            if( (A1_phonebook["File name"] ==pdf_file_name).sum() == 1):
                print(total_phonebook[total_phonebook["File name"] == labeled_file_name])
            else:
                continue
            
            #labeled file
            labeled_file = pd.read_excel(path_label)

            exit()
            #output file 
            for output_file_name in os.listdir(self.output_folder_path):

                print(output_file_name)    
                # if(len(file_name[:-4]) <= len(output_file_name)  and file_name[:-4] is output_file_name[:len(file_name[:-4])]):
                #     print(self.output_folder_path, " :  ", path_label)

def pipeline(pdf_path_list:list[str], output_folder_path: str,hidden_progress_bar = True,evaluater:evaluator=None):
    # #hyper param
    # treshold = 0.7 
    # keywords = ["bezoldiging", "wnt"]
    # minNumRowsMatched = 10
    # tesseract_cmd_path = r'D:/CODING/Tesseract-OCR/tesseract.exe'
    
        
    # Extractor = a1checkerMain.extractor()
    # checker = a1checkerMain.a1checker()

    # wrappedPdfs =[checker.is1aOrNot(pdfobj,treshold,minNumRowsMatched) for pdfobj in Extractor.extractFromPathList(pdf_path_list)]

    # for wrappedPDF in wrappedPdfs:
    #     pdf_path = wrappedPDF.file_path
    #     candidate_finder = speedy_candidates.candidates(keywords)
    #     #candidate pages 
    #     candidate_pages = candidate_finder.get_candidates(pdf_path,hide_progress_bar=hidden_progress_bar)

    #     for pagenumber in candidate_pages:     
    #         #exact match 
    #         exact_match_table,isExactMatch = exactmatch_whitespace.extract_data_from_pdf(pdf_path,pagenumber,minNumRowsMatched)
            
    #         if(isExactMatch):
    #             wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=True,csv_path="",csv_method="exact white space",tables=exact_match_table)
    #         else: #not exact match 
    #             whiteSpace(pdf_path,pagenumber,wrappedPDF)

    #     if(not wrappedPDF.has1ATable):
            
    #         for pagenum in tqdm(candidate_finder.needsOCR(pdf_path,hidden_progress_bar),ascii=True,desc="OCR"):
    #             # Create an instance of SearchablePDFConverter
    #             pdf_converter = scannedConvert.SearchablePDFConverter(pdf_path, tesseract_cmd_path)

    #             # Example 2: Convert a specific page of the PDF to a searchable PDF with post-processing
    #             searchable_pdf_page = pdf_converter.convert_to_searchable_pdf_page(pagenum)

    #             # Save the output searchable PDF for the specific page to a file
    #             searchable_pdf_page_output_path = f'tempSearchable.pdf'
    #             searchable_pdf_page.save(searchable_pdf_page_output_path)
    #             whiteSpace("tempSearchable.pdf",pagenum,wrappedPDF)
                
    # for pdf in tqdm(wrappedPdfs):
    #     for page in pdf.pages:
    #         if page.has_1a_table:
    #             if type(page._tables) is list:
    #                 for tablenum, table in enumerate(page._tables):
    #                     csv_path = os.path.join(output_folder_path, pdf.file_name[:-4]+str(page.page_number+tablenum)+".csv")
    #                     table.to_csv(csv_path)
    #                     page.csv_path = csv_path
    #             else:
    #                 csv_path = os.path.join(output_folder_path, str(pdf.file_name[:-4] + str(page.page_number)+".csv"))
    #                 page.csv_path = csv_path
    #                 page._tables.to_csv(csv_path)

    if(evaluater is not None):
        subprocess.run(["clear"])
        evaluater.compare_to_all()
        exit()
    debug_gui = debugger.PDFViewer(wrappedPdfs)
    debug_gui.run()



if __name__ == "__main__":
    """
    no parameters when called: it runs UI.
    if pipeline is called with ui-off <pdf foldername> <output path> <label path> <a1tablePagePhoneBook path>
    

    example:
    python pipeline.py ui-off pdfs /home/hal9000/Documents/github/CIBG-WNT-Parser/src_phase3/output_folder /home/hal9000/Documents/github/CIBG-WNT-Parser/labeled_files_2 /home/hal9000/Documents/github/CIBG-WNT-Parser/src_phase3/DataPhase3LabeledDocs.xlsx

    """
    command = sys.argv[-5]
    pdf_folder_name = sys.argv[-4] #NOT A PATH ONLY A NAME!!!!
    output_folder_path = sys.argv[-3]
    label_path = sys.argv[-2]
    a1tablePagePhoneBook_path = sys.argv[-1]
    
    if(len(sys.argv) == 6 and command == "ui-off"):
        print("no UI")

        extracter = a1checkerMain.extractor()
        pdf_path_list = [path_name[0] for path_name in extracter.recursiveFilePathIterator(pdf_folder_name)]
        evaluater = evaluator(a1tablePagePhoneBook_path,output_folder_path,label_path)

        pipeline(pdf_path_list,output_folder_path,False,evaluater=evaluater)



    else:
        root = TkinterDnD.Tk()
        app = PDFProcessorApp(root,pipeline)
        root.mainloop()