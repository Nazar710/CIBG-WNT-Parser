import fitz  # PyMuPDF
import re

def getUniqueKeywordRegion(pdf_path, keywords, target_page):
    unique_keyword_coordinates = []

    pdf_document = fitz.open(pdf_path)

    if not (0 <= target_page < pdf_document.page_count):
        print(f"Invalid target_page value. It should be in the range [0, {pdf_document.page_count - 1}]")
        target_page = 0

    page = pdf_document[target_page]

    for keyword in keywords:
        keyword_instances = page.search_for(keyword)
        unique_keyword_coordinates.extend(set(keyword_instances))

    pdf_document.close()
    return list(unique_keyword_coordinates)

def FinderAlgorithm(pdf_path, keywords, target_page):
    def find_salary_coordinates(keyword_coordinates):
        # Initialize variables to store the found instances
        bezoldiging_instances = []

        # Find instances of 'Bezoldiging' keyword
        for keyword_instance in keyword_coordinates:
            if " Bezoldiging " in page.get_text("text", clip=keyword_instance):
                bezoldiging_instances.append(keyword_instance)

        return bezoldiging_instances

    pdf_document = fitz.open(pdf_path)
    name_coordinates = {}
    box_coordinates = []
    salary_coordinates_list = []
    text_region_coordinates_list = []
    result_list = []
    used_name_instances = set()
    x_offset, y_offset, width_offset, height_offset = -5, 1, 30, 1

    if not (0 <= target_page < pdf_document.page_count):
        print(f"Invalid target_page value. It should be in the range [0, {pdf_document.page_count - 1}]")
        target_page = 0

    page = pdf_document[target_page]
    
    def extract_text_in_region(name, salary_coordinates):
        rect_for_extraction = (
            name_coordinates[name].x0 + x_offset,
            salary_coordinates.y0 + y_offset,
            name_coordinates[name].x1 + width_offset,
            salary_coordinates.y1 + height_offset
        )
        return page.get_text("text", clip=rect_for_extraction)

    def extract_number_from_text(text_in_region):
        match = re.search(r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)", text_in_region)
        if match:
            numeric_text = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(numeric_text)
            except ValueError:
                print(f"Error converting numeric text to number: {numeric_text}")
        return None

    for keyword in keywords:
        keyword_coordinates = getUniqueKeywordRegion(pdf_path, [keyword], target_page)
        bezoldiging_instances = find_salary_coordinates(keyword_coordinates)

        for bezoldiging_instance in bezoldiging_instances:
            # You can customize the extraction of information based on your requirements
            text_in_region = page.get_text("text", clip=bezoldiging_instance)
            number_in_region = extract_number_from_text(text_in_region)

            print(f"Keyword: {keyword}")
            print(f"Text in Region: {text_in_region}")
            print(f"Number in Region: {number_in_region}")
            print("N-------------------------------------------------N")

            # Append relevant coordinates and information to result lists
            box_coordinates.append((
                bezoldiging_instance.x0 + x_offset,
                bezoldiging_instance.y0 + y_offset,
                bezoldiging_instance.x1 + width_offset,
                bezoldiging_instance.y1 + height_offset
            ))
            salary_coordinates_list.append((bezoldiging_instance.x0, bezoldiging_instance.y0,
                                           bezoldiging_instance.x1, bezoldiging_instance.y1))
            text_region_coordinates_list.append((
                bezoldiging_instance.x0 + x_offset,
                bezoldiging_instance.y0 + y_offset,
                bezoldiging_instance.x1 + width_offset,
                bezoldiging_instance.y1 + height_offset
            ))

    pdf_document.close()
    return box_coordinates, salary_coordinates_list, text_region_coordinates_list, result_list

# Example usage:
pdf_path = "pdfs/DigiMV2020_V253SRE45G_0_41244295_Jaarrekening_3193_Deventer Ziekenhuis (Stichting).pdf"
keywords = ["Bezoldiging"]  # Replace with your actual keywords
target_page = 31  # Replace with the desired target page

box_coordinates, salary_coordinates_list, text_region_coordinates_list, result_list = FinderAlgorithm(pdf_path, keywords, target_page)
print(box_coordinates)