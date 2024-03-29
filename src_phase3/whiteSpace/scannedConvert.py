import fitz
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
import sys

class SearchablePDFConverter:
    """this class converts scanned pages of PDF documents into selectable PDFS while maintaining similar spacing"""
    def __init__(self, input_pdf_path, tesseract_cmd_path):
        self.input_pdf_path = input_pdf_path
        self.tesseract_cmd_path = tesseract_cmd_path

    def validate_paths(self) -> None:
        if(sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
            pass 
        else:

            if not os.path.isfile(self.input_pdf_path):
                raise FileNotFoundError(f"Input PDF not found at: {self.input_pdf_path}")

            if not os.path.isfile(self.tesseract_cmd_path):
                raise FileNotFoundError(f"Tesseract executable not found at: {self.tesseract_cmd_path}")

    def post_process_text(self, ocr_data: any, x_threshold:float=5, y_threshold:float=5) -> list:
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

    def convert_to_searchable_pdf(self, font_size:float=25, x_threshold:float=200, y_threshold:float=200) -> fitz.Document:
        
        if(sys.platform.startswith('linux') or sys.platform.startswith("darwin")):
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

    def convert_to_searchable_pdf_page(self, page_number: int, font_size: int=15, x_threshold:float=150, y_threshold:float=10) -> fitz.Document:
        if(sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
            pass 
        else:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
        self.validate_paths()

        # Step 1: Convert the specified page of the scanned PDF to an image
        image = convert_from_path(self.input_pdf_path, first_page=page_number, last_page=page_number)[0]

        # Step 2: Perform OCR on the image and create a searchable PDF for the specified page
        pdf_writer = fitz.open()

        # Perform OCR on the image with detailed data !!!! deleted lang = 'nld'in
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Post-process the OCR data to group words that are close in proximity
        grouped_text = self.post_process_text(ocr_data, x_threshold, y_threshold)

        # Create a new page in the output PDF
        pdf_page = pdf_writer.new_page(width=image.width, height=image.height)

        # Insert the grouped text into the PDF page at its original position with adjusted font size
        for j, (x, y, w, h, text) in enumerate(grouped_text):
            pdf_page.insert_text((x, y), text, fontsize=font_size)

        # Return the final searchable PDF for the specified page
        return pdf_writer 


