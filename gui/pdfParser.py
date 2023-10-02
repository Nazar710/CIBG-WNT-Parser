import camelot 
import pandas as pd

# Define the path to the PDF file
pdf_file = (r"src/gui/test.pdf")

# Extract tables from the PDF file (returns a list of DataFrames)
tables = camelot.read_pdf(pdf_file, pages='all', multiple_tables=True)

# Assuming the table you provided is on the first page (index 0), you can access it like this:
table_df = tables[0]

# Optional: You can clean up the DataFrame if needed
# For example, you can remove rows with NaN values:
table_df.dropna(inplace=True)

# Specify the path for the CSV output file
csv_file = 'output_data.csv'

# Save the DataFrame to a CSV file
table_df.to_csv(csv_file, index=False)

print(f'Table data has been extracted and saved to {csv_file}')
