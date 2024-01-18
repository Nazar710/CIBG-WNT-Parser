import fitz
import pandas as pd
import numpy as np 
from IPython.display import display
import matplotlib as plt

def find_tables_from_page(pdf_path:str, page_number:int):
    pdf_document = fitz.open(pdf_path)
    
    if 0 < page_number <= pdf_document.page_count:
            page = pdf_document[page_number - 1]
            tables = page.find_tables()  
            if len(tables.tables)>0:
                print(tables.tables[0].bbox)
                
       
    
def extract_columns_from_bounds(pdf_path:str, page_number:int,x0, y0, x1, y1, y_tolerance = 7) -> tuple[pd.DataFrame,bool]:
        pdf_document = fitz.open(pdf_path)
        bounds = fitz.Rect(x0,y0,x1,y1)
        column_coords = []
        if 0 < page_number <= pdf_document.page_count:
            
            page = pdf_document[page_number - 1]
            # Create an empty DataFrame with specific columns
            df = pd.DataFrame(columns=["bedragen x € 1", "Functiegegevens", "en einde functievervulling in", "Omvang dienstverband (als deeltijdfactor in fte)", "Dienstbetrekking","Beloning plus belastbare onkostenvergoedingen", "Beloningen betaalbaar op termijn", "Subtotaal","Individueel toepasselijke bezoldigingsmaximum","-/- Onverschuldigd betaald en nog niet terugontvangen bedrag", "Bezoldiging", "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan","Toelichting op de vordering wegens onverschuldigde betaling"])

            # search_texts = ["bedragen x €","functiegegevens","aanvang en einde functievervulling in","omvang dienstverband (als deeltijdfactor in fte)","dienstbetrekking","beloningen betaalbaar op termijn","onkostenvergoedingen","subtotaal","bezoldigingsmaximum","/- onverschuldigd betaald en nog niet terugontvangen bedrag","bezoldiging","al dan niet is toegestaan","toelichting op de vordering wegens onverschuldigde betaling"]
            search_texts = ["Functiegegevens","Aanvang en einde functievervulling in 2020", "bedragen x € 1 "]
            # Flags to check if we are currently processing specific lines
            words = page.get_text("words")
            words_df = pd.DataFrame(columns = ["row","word", "x0", "x1", "y0", "y1", "instance"])
            furthest_x = 0
            for text in search_texts:
                text_instances = page.search_for(text, clip = bounds)
                for instance in text_instances:
                    if instance.x1 > furthest_x:
                        furthest_x = instance.x1
                        #the furthest x value of the row keywords should indicate our first column
                if len(text_instances) > 0:
                    instance_id = 0
                    for text_instance in text_instances:
                        x0 = text_instance.x0
                        y0 = text_instance.y0
                        x1 = text_instance.x1
                        y1 = text_instance.y1
                        "(x0, y0, x1, y1, word, block_no, line_no, word_no)"
                        for word in words:
                            if word[3]<=y1+y_tolerance and word[1]>= y0-y_tolerance and word[0]>=text_instance.x1:
                                words_df.loc[len(words_df.index)] = [text, word[4],word[0],word[2],word[1],word[3],instance_id]
                        instance_id = instance_id +1
                        # after_search_text = [word for word in words if y0-y_tolerance <= word[1] <= y1+y_tolerance and word[0] >= x1]
                        
                        # split_data = []
                        # current_data = []
                        # for i, word in enumerate(after_search_text):
                        #     if i > 0 and word[0] - after_search_text[i - 1][2] > x_threshold:
                        #         # If horizontal distance is larger than x_threshold, split here
                        #         split_data.append(' '.join(current_data))
                        #         current_data = [word[4]]
                        #     else:
                        #         current_data.append(word[4])
                        # print(word)
        print(words_df)
        #add 1 so that the line does not cross text
        column_coords.append(furthest_x + 2)
        p1 = fitz.Point(column_coords[0],bounds.y1)
        p2 = fitz.Point(column_coords[0],bounds.y0)
        page.draw_line(p1,p2)
        img = page.get_pixmap()
        img.save("test.jpg")
        guess_columns(words_df,2)
        return column_coords
    
def guess_columns(words_df,x_threshold):
    suggested_columns = []
    for index, row in words_df.iterrows():
        if row['instance'] == 0 and row['row'] == 'Functiegegevens':
            print(row)

if __name__ == "__main__":
    # Example usage
        pdf_path = "C:/Users/mathi/OneDrive/Documenten/Uni/CIBG-WNT-Parser/src_phase3/pdfs/testTables.pdf"
        #output_dataframe = extract_columns_from_pdf(pdf_path, 5)

        print("column: ", extract_columns_from_bounds(pdf_path, 6, x0=0, x1=402,y0=110,y1=373))
        # print(output_dataframe)
        
        # Save the DataFrame to a CSV file
        # output_dataframe[0].to_csv("test_exact", index=False)
        