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
import numpy as np 

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
        wrong_page_number_count = 0
        false_positive_a1_table = 0

        for path_output_file,file_name in a1checkerMain.extractor.recursiveFilePathIterator(self.output_folder_path,["csv"]):
            pdf_file_name =file_name[:-4].split("=")[-2]+".pdf"
            pdf_table_page_num = file_name[:-4].split("=")[-1]
            
            #check if it has an a1 table
            if( (A1_phonebook["File name"] ==pdf_file_name).sum() == 1):
                ground_truth_page_num = A1_phonebook["Pages"][A1_phonebook["File name"] ==pdf_file_name].values[0]
                if(pdf_table_page_num != ground_truth_page_num):
                    wrong_page_number_count += 1
            else:
                false_positive_a1_table += 1
                continue
            
            #output file
            output_file = pd.read_csv(path_output_file,index_col=0)

            #labeled_file
            label_file = pd.read_excel(os.path.join(self.labelled_folder_path,pdf_file_name[:-4]+".pdf.xlsx"))

            """
            columns output_file:
            Name', 'Bezoldiging', 'Functie', 'functievervullingString','Dienstverband', 'Dienstbetrekking', 'Beloning', 'Beloningen',
            'Subtotaal', 'Bezoldigingsmaximum', 'Onverschuldigd', 'Overschrijding','Toelichting'
            """

            #NAME
            set_names_found = set(output_file["Name"])
            set_names_labelled = set(label_file.iloc[[0],1:].values[0]).union(set(label_file.iloc[[19],1:].values[0]))
            

            #results name matching
            num_names_correct = len(set_names_found.intersection(set_names_labelled))
            num_missing_names = len(set_names_labelled) - num_names_correct

            #BEZOLDIGING
            output_bezoldiging = output_file["Bezoldiging"]

            label_bezoldiging_first_year = label_file.iloc[[14],1:]
            label_bezoldiging_second_year = label_file.iloc[[31],1:]
            
            output_bezoldiging_vec = np.nan_to_num(output_bezoldiging.values)
            label_bezoldiging_vec = np.nan_to_num(pd.concat((label_bezoldiging_first_year,label_bezoldiging_second_year)).values.reshape(-1))

            #results  bezoldiging matching
            num_missing_bezoldigingen = len(label_bezoldiging_vec) - output_bezoldiging_vec
            num_matching_bezoldingen = (label_bezoldiging_vec[:len(output_bezoldiging_vec)] == output_bezoldiging_vec).sum()

            #FUNCTIE
            output_Functie = output_file["Functie"]
            
            print(label_file)
            # label_functie = pd.concat((label_file.iloc[[1],1:],)
                        
            exit()

def pipeline(pdf_path_list:list[str], output_folder_path: str,hidden_progress_bar = True,evaluater:evaluator=None):
    # # hyper param
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
    #                     csv_path = os.path.join(output_folder_path, pdf.file_name[:-4] +"="  +str(page.page_number+tablenum)+".csv")
    #                     table.to_csv(csv_path)
    #                     page.csv_path = csv_path
    #             else:
    #                 csv_path = os.path.join(output_folder_path, str(pdf.file_name[:-4] + "=" + str(page.page_number)+".csv"))
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