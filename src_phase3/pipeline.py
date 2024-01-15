import a1checker.a1checkerMain as a1checkerMain 
import whiteSpace.nameFind as nameFind
import whiteSpace.whitespaceMain as whitespaceMain
import candidatepageFinder.speedy_candidates as speedy_candidates

if __name__ == "__main__":
    #hyper param
    treshold = 0.7 
    keywords = ["bezoldiging", "wnt"]
    #pipeline
    Extractor = a1checkerMain.extractor()
    checker = a1checkerMain.a1checker()

    wrappedPdfs =[checker.is1aOrNot(pdfobj,treshold) for pdfobj in Extractor.extract("pdfs")]


    for wrappedPDF in wrappedPdfs:
        pdf_path = wrappedPDF.file_path

        #candidate pages 
        candidate_pages = speedy_candidates.candidates(keywords).get_candidates(pdf_path,hide_progress_bar=True)

        for pagenumber in candidate_pages:     
            #whitespace tables
            keyword_finder = nameFind.KeywordFinder(pdf_path)
            result = keyword_finder.find_keywords_with_context(pagenumber)
            keyword_finder.close()
            listofnames=result               

            pdf_processor = whitespaceMain.PDFProcessor()
            pdf_processor.process_pdf(pdf_path=pdf_path, target_page=pagenumber, names=listofnames)
            #page_number:int, selectable:bool, scanned:bool, has_1a_table:bool, csv_path:str,csv_method:str,tables:list[pd.DataFrame])
            tables = pdf_processor.return_results()
            wrappedPDF.add_page(page_number=pagenumber,selectable=True,scanned=False,has_1a_table=len(tables) > 0,tables=tables)
    

            

