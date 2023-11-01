import pdfplumber
import pandas as pd

# Function to extract tables from a PDF file
def extract_tables_from_pdf(pdf_file_path):
    """
    Extract tables from a PDF file using pdfplumber.

    Parameters:
        pdf_file_path (str): The file path of the PDF to be processed.

    Returns:
        list: A list of tables found in the PDF.
    """
    tables = []

    # Open the PDF file using pdfplumber
    with pdfplumber.open(pdf_file_path) as pdf:
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]

            # Extract text from the page
            page_text = page.extract_text()

            # Use pdfplumber's table extraction functionality
            extracted_tables = page.extract_tables()

            # Append the extracted tables to the result
            tables.extend(extracted_tables)

    return tables

# Function to save extracted tables as CSV files
def save_tables_to_csv(tables):
    """
    Save extracted tables as CSV files.

    Parameters:
        tables (list): A list of tables to be saved as CSV files.
    """
    # Initialize a counter for naming CSV files
    table_counter = 1

    for table in tables:
        # Convert each table to a DataFrame
        df = pd.DataFrame(table)

        # Define a CSV file name for the table
        csv_file_name = f'table_{table_counter}.csv'

        # Save the DataFrame as a CSV file
        df.to_csv(csv_file_name, index=False)

        # Increment the table counter
        table_counter += 1

if __name__ == "__main__":
    pdf_file_path = 'src/gui/test.pdf'
    detected_tables = extract_tables_from_pdf(pdf_file_path)

    if detected_tables:
        save_tables_to_csv(detected_tables)
        print(f"{len(detected_tables)} tables extracted and saved as CSV files.")
    else:
        print("No tables found in the PDF.")
