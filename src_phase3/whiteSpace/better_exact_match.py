import fitz
import pandas as pd
import numpy as np 
from IPython.display import display
import matplotlib as plt

def find_tables_from_page(pdf_path:str, page_number:int):
    pdf_document = fitz.open(pdf_path)
    
    if 0 < page_number <= pdf_document.page_count:
            page = pdf_document[page_number - 1]
            tables = page.find_tables(vertical_strategy = "text", horizontal_strategy = "text", min_words_vertical = 3, min_words_horizontal = 1)  
            if len(tables.tables)>0:
                print(tables.tables[0].bbox)
                

    
def extract_columns_from_page(pdf_path:str, page_number:int, y_tolerance_name = 5, y_tolerance_rest = 5) -> tuple[pd.DataFrame,bool]:
        pdf_document = fitz.open(pdf_path)
        # bounds = fitz.Rect(x0,y0,x1,y1)
        if 0 < page_number <= pdf_document.page_count:
            
            page = pdf_document[page_number - 1]
            tabs = page.find_tables()
            if len(tabs.tables) > 0:
                tab = tabs[0]
                bounds = tab.bbox
            else:
                print("no tables found")
            # Create an empty DataFrame with specific columns
            df = pd.DataFrame(columns=["bedragen x € 1", "Functiegegevens", "en einde functievervulling in", "Omvang dienstverband (als deeltijdfactor in fte)", "Dienstbetrekking","Beloning plus belastbare onkostenvergoedingen", "Beloningen betaalbaar op termijn", "Subtotaal","Individueel toepasselijke bezoldigingsmaximum","-/- Onverschuldigd betaald en nog niet terugontvangen bedrag", "Bezoldiging", "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan","Toelichting op de vordering wegens onverschuldigde betaling"])

            # search_texts = ["bedragen x €","functiegegevens","aanvang en einde functievervulling in","omvang dienstverband (als deeltijdfactor in fte)","dienstbetrekking","beloningen betaalbaar op termijn","onkostenvergoedingen","subtotaal","bezoldigingsmaximum","/- onverschuldigd betaald en nog niet terugontvangen bedrag","bezoldiging","al dan niet is toegestaan","toelichting op de vordering wegens onverschuldigde betaling"]
            search_texts = ["Functiegegevens","Aanvang en einde functievervulling in 2020", "bedragen x € 1"]
            # Flags to check if we are currently processing specific lines
            words = page.get_text("words")
            words_df = pd.DataFrame(columns = ["row","word", "x0", "x1", "y0", "y1", "instance"])
            furthest_x = 0
            for text in search_texts:
                
                text_instances = page.search_for(text, clip = bounds)
                for instance in text_instances:
                    
                    if text == "bedragen x € 1":
                        bedragen_x1 = instance.x1
                        y_tolerance = y_tolerance_name
                    else:
                        y_tolerance = y_tolerance_rest
                    if text == "Functiegegevens":
                        functie_x1 = instance.x1
                        
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
                        
        #set our potential first columns: halfway between bedragen and the first instance of a name
        column_coords = []
        column_coords.append(bounds[0])
        column_coords.append(bounds[2])
        
        bedragen_df = words_df.loc[words_df['row'] == "bedragen x € 1"]
        x0_first_word = bedragen_df['x0'].min()
        first_column_name = (bedragen_x1 + x0_first_word)/2
        
        functie_df = words_df.loc[words_df['row'] == "Functiegegevens"]
        x0_first_word = functie_df['x0'].min()
        first_column_functie = (functie_x1 + x0_first_word)/2
        
        column_coords.append(first_column_name)
        
        new_columns = guess_columns_name(words_df, column_coords[-1],10)
        column_coords = column_coords + new_columns
        
        #print(words_df)
        page.draw_rect(bounds)
        name_columns = page.new_shape()  # start a new shape
        for coord in column_coords:
            p1 = fitz.Point(coord,bounds[3])
            p2 = fitz.Point(coord,bounds[1])
            page.draw_line(p1,p2)
        
        functie_columns = []
        functie_columns.append(first_column_functie)
        new_columns = guess_columns_functiegegevens(words_df,functie_columns[-1],10)
        functie_columns = functie_columns + new_columns
        
        img = page.get_pixmap()
        img.save("test.jpg")
        tabs = page.find_tables(vertical_lines = tuple(column_coords))
        tabs[0].to_pandas().to_csv("extracted.csv")
        
        return column_coords
        
    
def guess_columns_name(words_df,start_x, x_threshold):
    suggested_columns = []
    names = []
    potential_name = ""
    x_end = start_x
    for index, row in words_df.iterrows():
        if row['row'] == "bedragen x € 1":
            if potential_name == "" or row['x0'] - x_end  < x_threshold:
                potential_name = potential_name + " " + row['word']
                x_end = row['x1']
            else:
                suggested_columns.append((x_end+row['x1'])/2)
                names.append(potential_name)
                potential_name = row['word']
                x_end = row['x1']
    names.append(potential_name)
    print(names)
    return suggested_columns

def guess_columns_functiegegevens(words_df,start_x, x_threshold):
    suggested_columns = []
    functie_names = []
    potential_functie = ""
    x_end = start_x
    for index, row in words_df.iterrows():
        if row['row'] == "Functiegegevens":
            if potential_functie == "" or row['x0'] - x_end  < x_threshold:
                potential_functie = potential_functie + " " + row['word']
                x_end = row['x1']
            else:
                suggested_columns.append((x_end+row['x1'])/2)
                functie_names.append(potential_functie)
                potential_functie = row['word']
                x_end = row['x1']
    functie_names.append(potential_functie)
    print(functie_names)
    return suggested_columns
            

if __name__ == "__main__":
    # Example usage
        pdf_path = "src_phase3/pdfs/testTables.pdf"
        #output_dataframe = extract_columns_from_pdf(pdf_path, 5)

        columns = extract_columns_from_page(pdf_path, 6)
        # print(output_dataframe)
        print(columns)

        # Save the DataFrame to a CSV file
        # output_dataframe[0].to_csv("test_exact", index=False)
        