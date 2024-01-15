#!/usr/bin/env python
# coding: utf-8

# In[91]:


import fitz
import pandas as pd
import numpy as np 

def extract_data_from_pdf(pdf_path:str, page_number:int,minNumRowsMatched:int) -> tuple[pd.DataFrame,bool]:
    pdf_document = fitz.open(pdf_path)
    
    if 0 < page_number <= pdf_document.page_count:
        page = pdf_document[page_number - 1]
        
        # Extract text from the page
        text = page.get_text("text")
        
        # Split the text into lines
        lines = text.split('\n')
        
        # Filter out empty lines
        lines = [line.strip() for line in lines if line.strip()]

        # Extract data from the lines
        data_lines = lines

        # Create an empty DataFrame with specific columns
        df = pd.DataFrame(columns=["bedragen x € 1", "Functiegegevens", "en einde functievervulling in", "Omvang dienstverband (als deeltijdfactor in fte)", "Dienstbetrekking","Beloning plus belastbare onkostenvergoedingen", "Beloningen betaalbaar op termijn", "Subtotaal","Individueel toepasselijke bezoldigingsmaximum","-/- Onverschuldigd betaald en nog niet terugontvangen bedrag", "Bezoldiging", "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan","Toelichting op de vordering wegens onverschuldigde betaling"])

        # Flags to check if we are currently processing specific lines
        is_bedragen_line = False
        is_functiegegevens_line = False
        is_subtotaal_line = False
        is_Dienstbetrekking_line = False
        is_Aanvang_line = 0 
        is_onko_line = False
        is_betaalbaar_line = False
        is_bezoldingsmax_line = False
        is_nogniet_line = False
        is_bezold_line = False
        is_hetbedrag_line = False
        is_toelichting_line = False
        is_omvang_line = False

        counter = 0

        # Iterate through lines and assign values to the respective columns
        for line in data_lines:
            if "bedragen x €" in line:
                # Set the flag to True when "bedragen x €" is encountered
                is_bedragen_line = True
                counter += 1
                
            elif is_bedragen_line:
                # Assign the value to the "bedragen x € 1" column and reset the flag
                df.loc[0, "bedragen x € 1"] = line
                is_bedragen_line = False
                
            if "Functiegegevens" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_functiegegevens_line = True
                counter += 1

                
            elif is_functiegegevens_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Functiegegevens"] = line
                is_functiegegevens_line = False
                
                
            if "en einde functievervulling in" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_Aanvang_line = 1
                counter += 1
                
            elif is_Aanvang_line == 1:
                 is_Aanvang_line = 2
                
            elif is_Aanvang_line == 2:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "en einde functievervulling in"] = line 
                is_Aanvang_line = 0 
                
                
            if "Omvang dienstverband (als deeltijdfactor in fte)" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_omvang_line = True
                counter += 1
                
            elif is_omvang_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Omvang dienstverband (als deeltijdfactor in fte)"] = line
                is_omvang_line = False
                
                
                
                
                
            if "Dienstbetrekking" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_Dienstbetrekking_line = True
                counter += 1
                
            elif is_Dienstbetrekking_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Dienstbetrekking"] = line
                is_Dienstbetrekking_line = False
                
                
            if "onkostenvergoedingen" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_onko_line = True
                counter += 1
                
            elif is_onko_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Beloning plus belastbare onkostenvergoedingen"] = line
                is_onko_line = False
                
                
            if "Beloningen betaalbaar op termijn" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_betaalbaar_line = True
                counter += 1
                
            elif is_betaalbaar_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Beloningen betaalbaar op termijn"] = line
                is_betaalbaar_line = False             
            
                
            if "Subtotaal" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_subtotaal_line = True
                counter += 1
                
            elif is_subtotaal_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Subtotaal"] = line
                is_subtotaal_line = False
                
                
            if "bezoldigingsmaximum" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_bezoldingsmax_line = True
                counter += 1
                
            elif is_bezoldingsmax_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Individueel toepasselijke bezoldigingsmaximum"] = line
                is_bezoldingsmax_line = False
                
                
            
            if "-/- Onverschuldigd betaald en nog niet terugontvangen bedrag" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_nogniet_line = True
                counter += 1
                
            elif is_nogniet_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "-/- Onverschuldigd betaald en nog niet terugontvangen bedrag"] = line
                is_nogniet_line = False
                
                
            
            if "Bezoldiging" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_bezold_line = True
                counter += 1
                
            elif is_bezold_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Bezoldiging"] = line
                is_bezold_line = False
                
                
            
            if "al dan niet is toegestaan" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_hetbedrag_line = True
                counter += 1
                
            elif is_hetbedrag_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan"] = line
                is_hetbedrag_line = False
                
                
            
            if "Toelichting op de vordering wegens onverschuldigde betaling" in line:
                # Set the flag to True when "Functiegegevens" is encountered
                is_toelichting_line = True
                counter += 1
                
            elif is_toelichting_line:
                # Assign the value to the "Functiegegevens" column and reset the flag
                df.loc[0, "Toelichting op de vordering wegens onverschuldigde betaling"] = line
                is_toelichting_line = False
                
                
        pdf_document.close()
        return df,counter > minNumRowsMatched
    
    
    
    else:
        print(f"Invalid page number: {page_number}")
        return None,None



if __name__ == "__main__":

    # Example usage
    pdf_path = "DigiMV2021_D378NP2TA9_1_30202982_Overig_18115_Het_Jagerhuis_B.V..pdf"
    page_number = 1  # Replace with the desired page number
    output_dataframe = extract_data_from_pdf(pdf_path, page_number)


    print(output_dataframe)
        
    # Save the DataFrame to a CSV file
    output_dataframe.to_csv("output_fileAAA.csv", index=False)
    