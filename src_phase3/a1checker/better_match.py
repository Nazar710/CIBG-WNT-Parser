import fitz
import pandas as pd
import numpy as np 
from IPython.display import display
import matplotlib as plt
import pdfplumber
                
class better_match():
    def __init__(self):
        self.search_texts = ["Functiegegevens", "bedragen x € 1"]
        self.exact_data_points = [
        "Bedragen x € 1",
        "Functiegegevens",
        "Aanvang en einde functievervulling in 2023",
        "Omvang dienstverband (als deeltijdfactor in fte)",
        "Dienstbetrekking",
        "Beloning plus belastbare onkostenvergoedingen",
        "Beloningen betaalbaar op termijn",
        "Subtotaal",
        "Individueel toepasselijke bezoldigingsmaximum",
        "-/- Onverschuldigd betaald en nog niet terugontvangen bedrag",
        "Bezoldiging",
        "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan",
        "reden waarom de overschrijding al dan niet is toegestaan",
        "Toelichting op de vordering wegens onverschuldigde betaling"
        ]
        self.data_points = [
        "bedragen", 
        "gegevens",
        "Functie",
        "Aanvang en einde functievervulling",
        "Omvang dienstverband",
        "(als deeltijdfactor in fte)"
        "Dienstbetrekking",
        "Beloning plus belastbare onkostenvergoedingen",
        "Beloning",
        "Subtotaal",
        "Individueel",
        "Onverschuldigd","terugontvangen"
        "Bezoldiging",
        "overschrijding", "toegestaan"
        "Toelichting op de vordering wegens onverschuldigde betaling", "totale", "totaal"
        ]
    def get_tables(self,pdf_path:str, page_number:int, y_tolerance = 5,column_strategy = "name",min_rows = 10, min_cols = 2):
        """finds tables by using pymupdf's table extractor and giving it columns inferred from either the names following
        the bedragen line or the functie following the functiegegevens line. Outputs a list of dfs filtered by keywords and a list of dfs
        filtered by exactly matching the 1a table"""
        dfs_linestrat = self.extract_tables_from_page(pdf_path,page_number,y_tolerance,column_strategy,horizontal_strategy="lines")
        dfs_textstrat = self.extract_tables_from_page(pdf_path,page_number,y_tolerance,column_strategy,horizontal_strategy="text")
        #filter out irrelevant rows based on keywords
        keywords_dfs = []
        keywords_dfs = keywords_dfs + self.process_dfs(dfs_linestrat)
        keywords_dfs = keywords_dfs + self.process_dfs(dfs_textstrat)
        keywords_dfs = [df for df in keywords_dfs if len(df) >= min_rows and df.shape[1] >= min_cols]
        
        exact_dfs = []
        exact_dfs = exact_dfs + self.filter_exact_dfs(dfs_linestrat)
        exact_dfs = exact_dfs + self.filter_exact_dfs(dfs_textstrat)
        exact_dfs = [df for df in exact_dfs if len(df) >= min_rows and df.shape[1] >= min_cols]
        return keywords_dfs, exact_dfs
    
    def extract_tables_from_page(self,pdf_path:str, page_number:int, y_tolerance = 5,column_strategy = "name",horizontal_strategy = "lines") -> tuple[pd.DataFrame,bool]:
        # read pdf document
        pdf_document = fitz.open(pdf_path)

            
        page = pdf_document[page_number - 1]
        extracted_dfs = []
        #find all tables in the page, first looking for ones that are explicitly outlined
        tabs = page.find_tables()
        
        if len(tabs.tables) == 0:
            #if no tables were found, try to find them by aligning text instead
            print("trying full text strategy")
            tabs = page.find_tables(strategy = "text")
            
        #if there was still no table found, return
        if len(tabs.tables) == 0:
            print("no tables on page")
            return
        
        #iterate over each table that was found
        for tab in tabs.tables:
            #limit our text search to within the found table
            bounds = tab.bbox
        
            # Flags to check if we are currently processing specific lines
            words = page.get_text("words")
            words_df = pd.DataFrame(columns = ["row","word", "x0", "x1", "y0", "y1"])
            
            for text in self.search_texts:
                #search for instances of the texts within the table
                text_instances = page.search_for(text, clip = bounds)
                if len(text_instances) == 0:
                    # if there is no row for functiegegevens or bedragen, return an empty list.
                    print(text, " was absent:", pdf_path, page_number)
                    break
        
                
                #note the furthest x coordinate of bedragen and functiegegevens
                instance = text_instances[0]
                if text == "bedragen x € 1":
                    bedragen_x1 = instance.x1
                    
                if text == "Functiegegevens":
                    functie_x1 = instance.x1

                x0 = instance.x0
                y0 = instance.y0
                x1 = instance.x1
                y1 = instance.y1
                "(x0, y0, x1, y1, word, block_no, line_no, word_no)"
                for word in words:
                    #if a word is within the y tolerance on the same line as our instance and it appears at a further
                    # x coordinate, add it to the words dataframe together with its coordinates
                    if word[3]<=y1+y_tolerance and word[1]>= y0-y_tolerance and word[0]>=instance.x1:
                        words_df.loc[len(words_df.index)] = [text, word[4],word[0],word[2],word[1],word[3]]
                        
                        
                        
            #set our boundary columns: the beginning and end of the table
            column_coords = []
            column_coords.append(bounds[0])
            column_coords.append(bounds[2])
            
            #find the coordinate for the first instance of data after bedragen
            bedragen_df = words_df.loc[words_df['row'] == "bedragen x € 1"]
            x0_first_name = bedragen_df['x0'].min()

            
            #find the coordinate for the first instance of data after functiegegevens
            functie_df = words_df.loc[words_df['row'] == "Functiegegevens"]
            x0_first_functie = functie_df['x0'].min()

            #create our first column, before both the first name and the first functie data point
            column_coords.append(min(x0_first_name,x0_first_functie)-5)
        

            name_columns = self.guess_columns_name(words_df, column_coords[-1],5)
            
            functie_columns = self.guess_columns_functiegegevens(words_df,column_coords[-1],5)
            
            if column_strategy == "name":
                column_coords = column_coords + name_columns
            elif column_strategy == "functie":
                column_coords = column_coords + functie_columns
            
            
            # uncomment to draw the inferred columns
            
            # for coord in column_coords:
            #     p1 = fitz.Point(coord,bounds[3])
            #     p2 = fitz.Point(coord,bounds[1])
            #     page.draw_line(p1,p2)
            # page.draw_rect(bounds)
            # img = page.get_pixmap()
            # img.save("test3.jpg")
            
            tabs = page.find_tables(vertical_strategy = "explicit", vertical_lines = column_coords, horizontal_strategy = horizontal_strategy)
            for table in tabs:
                extracted_dfs.append(table.to_pandas())
            
                
        for i, df in enumerate(extracted_dfs):
            
            filename = f"extracted_{i}.csv"
            # Save the DataFrame to a CSV file
            df.to_csv(filename, index=False)
        return extracted_dfs
            
        
    def guess_columns_name(self,words_df,start_x, x_threshold):
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
        return suggested_columns

    def guess_columns_functiegegevens(self,words_df,start_x, x_threshold):
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
        return suggested_columns
    
    def process_dfs(self,dfs):
        filtered_dfs = []  # List to store filtered DataFrames

        for df in dfs:
            # Initialize a Series of False values
            mask = pd.Series([False] * len(df))

            # Update the mask if the first column contains any of the strings in self.data_points
            for string in self.data_points:
                mask = mask | df.iloc[:, 0].str.contains(string, na=False,case = False)

            # Filter the DataFrame using the mask
            filtered_df = df[mask]
            filtered_dfs.append(filtered_df)
            
        return filtered_dfs
    
    def filter_exact_dfs(self, dfs):
        filtered_dfs = []  # List to store filtered DataFrames

        for df in dfs:
            # Initialize a Series of False values
            mask = pd.Series([False] * len(df))
            first_col_lower = df.iloc[:, 0].str.lower()
            # Update the mask if the first column contains any of the strings in self.data_points
            for string in self.exact_data_points:
                mask = mask | (first_col_lower == string.lower())
            # Filter the DataFrame using the mask
            filtered_df = df[mask]
            filtered_dfs.append(filtered_df)
            
        return filtered_dfs
if __name__ == "__main__":
    # Example usage
        pdf_path = "src_phase3/pdfs/testTables.pdf"
        better_matcher = better_exact_match()
        better_matcher.extract_tables_from_page(pdf_path,1,horizontal_strategy="text")
        
        # print(output_dataframe)
    

        # Save the DataFrame to a CSV file
        # output_dataframe[0].to_csv("test_exact", index=False)
            