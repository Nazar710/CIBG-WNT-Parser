import os
import fitz  # PyMuPDF
import pandas as pd

# Import custom FinderAlgorithm from find module
from FindBezoldiging import FinderAlgorithm
from NameFinder import PDFTextExtractor, detect_high_probability_names, merge_keywords_in_range
from scannedConvert import SearchablePDFConverter

# Function to process all PDF files in a folder
def process_pdfs(df, pdf_folder, output_csv_path):
    results_data = []

    # Iterate through each entry in the DataFrame
    for index, row in df.iterrows():
        pdf_file_name = row['FileName']
        page_number = row['Pagenumber']

        # Construct the full path to the PDF file
        pdf_path = os.path.join(pdf_folder, f"{pdf_file_name}")

        # Check if the PDF file exists
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found: {pdf_path}")
            continue

        # Extract text from the specified page
        # pdf_extractor = PDFTextExtractor(pdf_path, page_number, 1)
        word_space_size = 500
        model_path = 'name_detection_model.h5'
        tokenizer_path = 'tokenizer.pkl'

        high_prob_df = detect_high_probability_names(pdf_path, word_space_size, page_number, model_path, tokenizer_path)

        # Scanned Paper
        if len(high_prob_df) == 0:
            # Replace 'path_to_tesseract_executable' with the actual path to your Tesseract OCR executable
            tesseract_cmd_path = r'D:/CODING/Tesseract-OCR/tesseract.exe'

            # Create an instance of SearchablePDFConverter
            pdf_converter = SearchablePDFConverter(pdf_path, tesseract_cmd_path)

            # Example 2: Convert a specific page of the PDF to a searchable PDF with post-processing
            searchable_pdf_page = pdf_converter.convert_to_searchable_pdf_page(page_number)

            # Save the output searchable PDF for the specific page to a file
            pdf_path = f'tempSearchable.pdf'
            searchable_pdf_page.save(pdf_path)
            page_number = 1
            high_prob_df = detect_high_probability_names(pdf_path, word_space_size, page_number, model_path,
                                                         tokenizer_path)

        # Call FinderAlgorithm with the extracted sentences
        box_coordinates, salary_coordinates_list, text_region_coordinates_list, result_list = FinderAlgorithm(pdf_path,
                                                                                                                high_prob_df[
                                                                                                                    'Name'],
                                                                                                                page_number - 1)

        # Create a DataFrame from the result_list
        result_df = pd.DataFrame(result_list, columns=['Name', 'Bezoldiging'])

        # Add additional columns for FileName and PageNumber
        result_df['filename'] = pdf_file_name
        result_df['PageNumber'] = page_number

        # Append the DataFrame to the results_data list
        results_data.append(result_df)

    # Concatenate all DataFrames in the results_data list
    final_result_df = pd.concat(results_data, ignore_index=True)

    # Save the results to a CSV file
    final_result_df.to_csv(output_csv_path, index=False)
    print(f"Results saved to: {output_csv_path}")


print("FINDING NAME AND KEYWORD ..........")

# # Example usage
# csv_path = "CSV/AllDatainput.csv"
# pdf_folder = "pdfs"
# output_csv_path = "CSV/AllDataResults.csv"

# # Read the CSV file into a DataFrame
# csv_data = pd.read_csv(csv_path)

# # Process all PDFs in the folder based on the DataFrame
# process_pdfs(csv_data, pdf_folder, output_csv_path)
