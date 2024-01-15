import fitz
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

class SearchablePDFConverter:
    def __init__(self, input_pdf_path, tesseract_cmd_path):
        self.input_pdf_path = input_pdf_path
        self.tesseract_cmd_path = tesseract_cmd_path

    def validate_paths(self):
        if not os.path.isfile(self.input_pdf_path):
            raise FileNotFoundError(f"Input PDF not found at: {self.input_pdf_path}")

        if not os.path.isfile(self.tesseract_cmd_path):
            raise FileNotFoundError(f"Tesseract executable not found at: {self.tesseract_cmd_path}")

    def post_process_text(self, ocr_data, x_threshold=5, y_threshold=5):
        grouped_text = []

        for (x, y, w, h, text) in zip(
            ocr_data['left'], ocr_data['top'], ocr_data['width'], ocr_data['height'], ocr_data['text']
        ):
            if text.strip() != '':
                # Check if the current word is close enough to the last one in terms of X and Y coordinates
                if grouped_text and abs(grouped_text[-1][0] - x) < x_threshold and abs(grouped_text[-1][1] - y) < y_threshold:
                    # Merge the current word with the last one
                    grouped_text[-1] = (grouped_text[-1][0], grouped_text[-1][1], w, max(grouped_text[-1][3], h), grouped_text[-1][4] + ' ' + text)
                else:
                    # Add the current word as a new group
                    grouped_text.append((x, y, w, h, text))

        return grouped_text

    def convert_to_searchable_pdf(self, font_size=25, x_threshold=200, y_threshold=200):
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
        self.validate_paths()

        # Step 1: Convert each page of the scanned PDF to images
        images = convert_from_path(self.input_pdf_path)

        # Step 2: Perform OCR on each image and create a searchable PDF
        pdf_writer = fitz.open()

        for i, image in enumerate(images):
            # Perform OCR on the image with detailed data
            ocr_data = pytesseract.image_to_data(image, lang='nld', output_type=pytesseract.Output.DICT)

            # Post-process the OCR data to group words that are close in proximity
            grouped_text = self.post_process_text(ocr_data, x_threshold, y_threshold)

            # Create a new page in the output PDF
            pdf_page = pdf_writer.new_page(width=image.width, height=image.height)

            # Insert the grouped text into the PDF page at its original position with adjusted font size
            for j, (x, y, w, h, text) in enumerate(grouped_text):
                pdf_page.insert_text((x, y), text, fontsize=font_size)

        # Return the final searchable PDF
        return pdf_writer

    def convert_to_searchable_pdf_page(self, page_number, font_size=5, x_threshold=150, y_threshold=10):
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
        self.validate_paths()

        # Step 1: Convert the specified page of the scanned PDF to an image
        image = convert_from_path(self.input_pdf_path, first_page=page_number, last_page=page_number)[0]

        # Step 2: Perform OCR on the image and create a searchable PDF for the specified page
        pdf_writer = fitz.open()

        # Perform OCR on the image with detailed data
        ocr_data = pytesseract.image_to_data(image, lang='nld', output_type=pytesseract.Output.DICT)

        # Post-process the OCR data to group words that are close in proximity
        grouped_text = self.post_process_text(ocr_data, x_threshold, y_threshold)

        # Create a new page in the output PDF
        pdf_page = pdf_writer.new_page(width=image.width, height=image.height)

        # Insert the grouped text into the PDF page at its original position with adjusted font size
        for j, (x, y, w, h, text) in enumerate(grouped_text):
            pdf_page.insert_text((x, y), text, fontsize=font_size)

        # Return the final searchable PDF for the specified page
        return pdf_writer

# Example usage of the SearchablePDFConverter class

# Replace 'path_to_input_pdf.pdf' with the actual path to your input PDF file
input_pdf_path = 'pdfs/DigiMV2020_NZZ7VU7B27_0_27047100_Jaarrekening_9355_Kessler Stichting.pdf'

# Replace 'path_to_tesseract_executable' with the actual path to your Tesseract OCR executable
tesseract_cmd_path = r'D:/CODING/Tesseract-OCR/tesseract.exe'

# Create an instance of SearchablePDFConverter
pdf_converter = SearchablePDFConverter(input_pdf_path, tesseract_cmd_path)

# Example 2: Convert a specific page of the PDF to a searchable PDF with post-processing
page_number_to_convert = 78  # Replace with the desired page number
searchable_pdf_page = pdf_converter.convert_to_searchable_pdf_page(page_number_to_convert)

# Save the output searchable PDF for the specific page to a file
searchable_pdf_page_output_path = f'tempSearchable.pdf'
searchable_pdf_page.save(searchable_pdf_page_output_path)
