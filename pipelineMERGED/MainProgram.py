import os
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from tqdm import tqdm

from MainFinder import process_pdfs


#THIS IS THE MAIN PROGRAM
#YOU CAN RUN THIS OR GUI
#HERE INPUT IS FOLDER
#GUI INPUT IS FILES



# Class for identifying WNT (Wet Normering Topinkomens) pages in PDFs based on keywords
class WNTPageIdentifier:
    def __init__(self, keywords=["bezoldiging", "beloning"]) -> None:
        self.keywords = keywords

    def __is_scanned_pdf(self, pdf_path):
        # Check if the PDF contains scanned images (non-selectable text)
        images = convert_from_path(pdf_path)
        for image in images:
            text = pytesseract.image_to_string(image)
            if text.strip():
                return True
        return False

    def __extract_text_from_pdf(self, pdf_path):
        # Extract text from a PDF using OCR
        images = convert_from_path(pdf_path)
        extracted_text = []
        for image in tqdm(images, ascii=True, desc="Extracting text"):
            text = pytesseract.image_to_string(image)
            extracted_text.append(text)
        return extracted_text

    def __identify_wnt_pages(self, pdf_path):
        # Identify pages containing WNT information based on keywords
        if self.__is_scanned_pdf(pdf_path):
            # If scanned PDF, use OCR for text extraction
            extracted_text = self.__extract_text_from_pdf(pdf_path)
        else:
            # If text is selectable, directly read the PDF text
            with open(pdf_path, 'rb') as pdf_file:
                extracted_text = [page.extract_text() for page in pdf_file.pages()]

        wnt_pages = []
        for i, text in enumerate(extracted_text):
            contains_all_keywords = all(keyword.lower() in text.lower() for keyword in self.keywords)
            if contains_all_keywords:
                wnt_pages.append(i + 1)  # Page numbers are usually 1-indexed

        return wnt_pages

    def process_folder(self, folder_path):
        wnt_info_list = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                wnt_pages = self.__identify_wnt_pages(pdf_path)

                if wnt_pages:
                    for page_number in wnt_pages:
                        wnt_info_list.append({
                            'FileName': filename,
                            'Pagenumber': page_number
                        })

        wnt_info_df = pd.DataFrame(wnt_info_list)
        return wnt_info_df

if __name__ == "__main__":
    # Example usage
    folder_path = "test"

    #HERE YOU RETURN DATAFRAME OF FILENAMES AND PAGE NUMBER

    wnt_identifier = WNTPageIdentifier()
    result_df = wnt_identifier.process_folder(folder_path)
    print(result_df)

    # CSV NAME for Results
    output_csv_path = "Results.csv"


    #HERE YOU get input the DATAFRAME of WNT FINDER and output CSV with WNT info

    # Process PDFs and create a CSV file
    process_pdfs(result_df, folder_path, output_csv_path)

    # Read the generated CSV file
    csv_data = pd.read_csv(output_csv_path)
