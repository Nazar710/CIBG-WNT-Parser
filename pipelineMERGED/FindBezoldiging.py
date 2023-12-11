import fitz  # PyMuPDF
import re

def FinderAlgorithm(pdf_path, names, target_page):
    def complete_name_instance(name_instance):
        if name_instance.x1 == page.rect.width:
            next_line_instances = page.search_for(name, clip=(name_instance.x0, 0, page.rect.width, page.rect.height))
            if next_line_instances:
                return fitz.Rect(name_instance.x0, name_instance.y0, next_line_instances[0].x1, next_line_instances[0].y1)
        return name_instance

    def find_salary_coordinates(name):
        # Initialize variables to store the found instances
        totaal_instances = []
        totale_instances = []
        bezoldiging_instances = []

        # Find instances of 'Totaal', 'Totale', and 'Bezoldiging' keywords
        for keyword in salary_keywords:
            if " Totaal " in keyword:
                totaal_instances = page.search_for(keyword, rect=name_coordinates[name])
            elif "Totale" in keyword:
                totale_instances = page.search_for(keyword, rect=name_coordinates[name])
            elif " Bezoldiging " in keyword:
                bezoldiging_instances = page.search_for(keyword, rect=name_coordinates[name])

        # Now max_y contains the updated maximum y-coordinate based on the conditions

        # Check for 'Bezoldiging' keyword instances
        for salary_instance in bezoldiging_instances:
            if max_y > salary_instance.y0 > name_coordinates[name].y1:
                text_in_region = extract_text_in_region(name, salary_instance)
                number_in_region = extract_number_from_text(text_in_region)

                if number_in_region is not None:
                    return salary_instance

        # Check for 'Totaal' keyword instances
        for salary_instance in totaal_instances:
            if max_y > salary_instance.y0 > name_coordinates[name].y1:
                text_in_region = extract_text_in_region(name, salary_instance)
                number_in_region = extract_number_from_text(text_in_region)

                if number_in_region is not None:
                    return salary_instance

        # If 'Totaal' keyword doesn't yield a number, check 'Totale' keyword
        for salary_instance in totale_instances:
            if max_y > salary_instance.y0 > name_coordinates[name].y1:
                text_in_region = extract_text_in_region(name, salary_instance)
                number_in_region = extract_number_from_text(text_in_region)

                if number_in_region is not None:
                    return salary_instance

        return None

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

    pdf_document = fitz.open(pdf_path)
    name_coordinates = {}
    box_coordinates = []
    salary_coordinates_list = []
    text_region_coordinates_list = []
    result_list = []
    used_name_instances = set()
    x_offset, y_offset, width_offset, height_offset = -5, 1, 30, 1
    salary_keywords = [" Totaal Bezoldiging ", " Totale Bezoldiging ", " Bezoldiging ", " Totaal ", " Totale "]

    if not (0 <= target_page < pdf_document.page_count):
        print(f"Invalid target_page value. It should be in the range [0, {pdf_document.page_count - 1}]")
        target_page = 0

    page = pdf_document[target_page]
    max_y = page.rect.height

    for name in names:
        name_instances_iter = page.search_for(name)

        if name_instances_iter:
            name_instance = complete_name_instance(name_instances_iter[0])
            name_coordinates[name] = name_instance
            used_name_instances.add(name_instance)

            salary_coordinates = find_salary_coordinates(name)

            if salary_coordinates:
                text_in_region = extract_text_in_region(name, salary_coordinates)
                number_in_region = extract_number_from_text(text_in_region)

                print(f"Name: {name}")
                print(f"Text in Region: {text_in_region}")
                print(f"Number in Region: {number_in_region}")
                print("N-------------------------------------------------N")

                result_list.append((name, number_in_region if number_in_region else text_in_region))
                box_coordinates.append((
                    name_coordinates[name].x0 + x_offset,
                    name_coordinates[name].y0 + y_offset,
                    name_coordinates[name].x1 + width_offset,
                    name_coordinates[name].y1 + height_offset
                ))
                salary_coordinates_list.append((salary_coordinates.x0, salary_coordinates.y0,
                                               salary_coordinates.x1, salary_coordinates.y1))
                text_region_coordinates_list.append((
                    name_coordinates[name].x0 + x_offset,
                    salary_coordinates.y0 + y_offset,
                    name_coordinates[name].x1 + width_offset,
                    salary_coordinates.y1 + height_offset
                ))
            else:
                print(f"Salary not found below {name}")
        else:
            print(f"{name} not found on page {target_page + 1}")

    pdf_document.close()
    return box_coordinates, salary_coordinates_list, text_region_coordinates_list, result_list

