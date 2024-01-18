import fitz  # PyMuPDF
import re

def FinderAlgorithm(pdf_path, names, target_page):
    def complete_name_instance(name_instance):
        if name_instance.x1 == page.rect.width:
            next_line_instances = page.search_for(name, rect=(name_instance.x0, 0, page.rect.width, page.rect.height))
            if next_line_instances:
                return fitz.Rect(name_instance.x0, name_instance.y0, next_line_instances[0].x1, next_line_instances[0].y1)
        return name_instance

    def find_salary_coordinates(name):
        # Initialize variables to store the found instances
        totaal_instances = []
        totale_instances = []
        bezoldiging_instances = []

        rect = fitz.Rect(name_coordinates[name])

        # Find instances of 'Totaal', 'Totale', and 'Bezoldiging' keywords
        for keyword in salary_keywords:
            if " Totaal " in keyword:
                totaal_instances = page.search_for(keyword, rect=rect)
            elif "Totale" in keyword:
                totale_instances = page.search_for(keyword, rect=rect)
            elif " Bezoldiging " in keyword:
                bezoldiging_instances = page.search_for(keyword, rect=rect)

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
    
    def find_function(name):
        # Initialize variable to store the found instances
        functie_instances = []
        rect = fitz.Rect(name_coordinates[name])

        # Find instances of 'Functie' keyword
        for keyword in ["Functie"]:
            functie_instances = page.search_for(keyword, rect=rect)

        # Check for 'Functie' keyword instances
        for functie_instance in functie_instances:
            if max_y > functie_instance.y0 > name_coordinates[name].y1:
                return functie_instance

        return None

    def find_bezoldigingsmaximum(name):
        # Initialize variable to store the found instances
        bezoldigingsmaximum_instances = []
        rect = fitz.Rect(name_coordinates[name])

        # Find instances of 'Bezoldigingsmaximum' keyword
        for keyword in ["Bezoldigingsmaximum"]:
            bezoldigingsmaximum_instances = page.search_for(keyword, rect=rect)

        # Check for 'Bezoldigingsmaximum' keyword instances
        for bezoldigingsmaximum_instance in bezoldigingsmaximum_instances:
            if max_y > bezoldigingsmaximum_instance.y0 > name_coordinates[name].y1:
                return bezoldigingsmaximum_instance

        return None
    def find_functievervulling(name):
        # Initialize variable to store the found instances
        functievervulling_instances = []
        rect = fitz.Rect(name_coordinates[name])

        # Find instances of 'Functievervulling' keyword
        for keyword in ["Functievervulling"]:
            functievervulling_instances = page.search_for(keyword, rect=rect)

        # Check for 'Functievervulling' keyword instances
        for functievervulling_instance in functievervulling_instances:
            if max_y > functievervulling_instance.y0 > name_coordinates[name].y1:
                return functievervulling_instance

        return None    
    
    def find_dienstverband(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        dienstverband_instances = []

        # Find instances of 'Dienstverband' keyword
        for keyword in ["Dienstverband"]:
            dienstverband_instances = page.search_for(keyword, rect=rect)

        # Check for 'Dienstverband' keyword instances
        for dienstverband_instance in dienstverband_instances:
            if max_y > dienstverband_instance.y0 > name_coordinates[name].y1:
                return dienstverband_instance

        return None    
    
    def extract_text_in_region(name, salary_coordinates):
        rect_for_extraction = (
            name_coordinates[name].x0 + x_offset,
            salary_coordinates.y0 + y_offset,
            name_coordinates[name].x1 + width_offset,
            salary_coordinates.y1 + height_offset
        )
        return page.get_text("text", clip=rect_for_extraction)


    def find_dienstbetrekking(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        dienstbetrekking_instances = []

        # Find instances of 'Dienstbetrekking' keyword
        for keyword in ["Dienstbetrekking"]:
            dienstbetrekking_instances = page.search_for(keyword, rect=rect)

        # Check for 'Dienstbetrekking' keyword instances
        for dienstbetrekking_instance in dienstbetrekking_instances:
            if max_y > dienstbetrekking_instance.y0 > name_coordinates[name].y1:
                return dienstbetrekking_instance

        return None    

    def find_beloning(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        beloning_instances = []

        # Find instances of 'Beloning' keyword
        for keyword in ["Beloning"]:
            beloning_instances = page.search_for(keyword, rect=rect)

        # Check for 'Beloning' keyword instances
        for beloning_instance in beloning_instances:
            if max_y > beloning_instance.y0 > name_coordinates[name].y1:
                return beloning_instance

        return None    

    def find_beloningen(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        beloningen_instances = []

        # Find instances of 'Beloningen' keyword
        for keyword in ["Beloningen"]:
            beloningen_instances = page.search_for(keyword, rect=rect)

        # Check for 'Beloningen' keyword instances
        for beloningen_instance in beloningen_instances:
            if max_y > beloningen_instance.y0 > name_coordinates[name].y1:
                return beloningen_instance

        return None    

    def find_subtotaal(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        subtotaal_instances = []

        # Find instances of 'Subtotaal' keyword
        for keyword in ["Subtotaal"]:
            subtotaal_instances = page.search_for(keyword, rect=rect)

        # Check for 'Subtotaal' keyword instances
        for subtotaal_instance in subtotaal_instances:
            if max_y > subtotaal_instance.y0 > name_coordinates[name].y1:
                return subtotaal_instance

        return None    

    def find_bezoldigingsmaximum(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        bezoldigingsmaximum_instances = []

        # Find instances of 'Bezoldigingsmaximum' keyword
        for keyword in ["Bezoldigingsmaximum"]:
            bezoldigingsmaximum_instances = page.search_for(keyword, rect=rect)

        # Check for 'Bezoldigingsmaximum' keyword instances
        for bezoldigingsmaximum_instance in bezoldigingsmaximum_instances:
            if max_y > bezoldigingsmaximum_instance.y0 > name_coordinates[name].y1:
                return bezoldigingsmaximum_instance

        return None    

    def find_onverschuldigd(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        onverschuldigd_instances = []

        # Find instances of 'Onverschuldigd' keyword
        for keyword in ["Onverschuldigd"]:
            onverschuldigd_instances = page.search_for(keyword, rect=rect)

        # Check for 'Onverschuldigd' keyword instances
        for onverschuldigd_instance in onverschuldigd_instances:
            if max_y > onverschuldigd_instance.y0 > name_coordinates[name].y1:
                return onverschuldigd_instance

        return None    

    def find_overschrijding(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        overschrijding_instances = []

        # Find instances of 'Overschrijding' keyword
        for keyword in ["Overschrijding"]:
            overschrijding_instances = page.search_for(keyword, rect=rect)

        # Check for 'Overschrijding' keyword instances
        for overschrijding_instance in overschrijding_instances:
            if max_y > overschrijding_instance.y0 > name_coordinates[name].y1:
                return overschrijding_instance

        return None    

    def find_toelichting(name):
        rect = fitz.Rect(name_coordinates[name])
        # Initialize variable to store the found instances
        toelichting_instances = []

        # Find instances of 'Toelichting' keyword
        for keyword in ["Toelichting"]:
            toelichting_instances = page.search_for(keyword, rect=rect)

        # Check for 'Toelichting' keyword instances
        for toelichting_instance in toelichting_instances:
            if max_y > toelichting_instance.y0 > name_coordinates[name].y1:
                return toelichting_instance

        return None


    

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
    result_list = []
    used_name_instances = set()
    x_offset, y_offset, width_offset, height_offset = -5, 1, 30, 1
    salary_keywords = [" Totaal Bezoldiging ", " Totale Bezoldiging ", " Bezoldiging ", " Totaal ", " Totale "]

    if not (0 <= target_page < pdf_document.page_count):
        print(f"Invalid target_page value. It should be in the range [0, {pdf_document.page_count - 1}]")
        target_page = 0

    page = pdf_document[target_page]
    max_y = page.rect.height
    foundNames=[]

    for nameX in names:
        name_instances_iterX = page.search_for(nameX)
        if name_instances_iterX:
            foundNames.append(nameX)

    for name in foundNames:
        name_instances_iter = page.search_for(name)

        if name_instances_iter:
            name_instance = complete_name_instance(name_instances_iter[0])
            name_coordinates[name] = name_instance
            used_name_instances.add(name_instance)

            
            functionString=""
            functievervullingString=""
            dienstverbandString=""
            dienstbetrekkingString=""
            beloningString =""
            beloningenString =""
            subtotaalString=""
            bezoldigingsmaximumString=""
            onverschuldigdString =""
            overschrijdingString =""
            toelichtingString =""
            text_in_region=""

            salary_coordinates = find_salary_coordinates(name)
            function_coordinates = find_function(name)
            bezoldigingsmaximum_coordinates = find_bezoldigingsmaximum(name)
            functievervulling_coordinates = find_functievervulling(name)
            dienstverband_coordinates = find_dienstverband(name)
            
            dienstbetrekking_coordinates = find_dienstbetrekking(name)
            beloning_coordinates = find_beloning(name)
            beloningen_coordinates = find_beloningen(name)
            subtotaal_coordinates = find_subtotaal(name)
            onverschuldigd_coordinates = find_onverschuldigd(name)
            overschrijding_coordinates = find_overschrijding(name)
            toelichting_coordinates = find_toelichting(name)

            if salary_coordinates:
                text_in_region = extract_text_in_region(name, salary_coordinates)
                number_in_region = extract_number_from_text(text_in_region)

                #print(f"Name: {name}")
                #print(f"Text in Region: {text_in_region}")
                #print(f"Number in Region: {number_in_region}")
                #print("N-------------------------------------------------N")
            
            if function_coordinates:
                functionString = extract_text_in_region(name, function_coordinates)

            if bezoldigingsmaximum_coordinates:
                bezoldigingsmaximumString = extract_text_in_region(name, bezoldigingsmaximum_coordinates)

            if functievervulling_coordinates:
                functievervullingString = extract_text_in_region(name, functievervulling_coordinates)

            if dienstverband_coordinates:
                dienstverbandString = extract_text_in_region(name, dienstverband_coordinates) 
           
            if dienstbetrekking_coordinates:
                dienstbetrekkingString = extract_text_in_region(name, dienstbetrekking_coordinates)

            if beloning_coordinates:
                beloningString = extract_text_in_region(name, beloning_coordinates)

            if beloningen_coordinates:
                beloningenString = extract_text_in_region(name, beloningen_coordinates)

            if subtotaal_coordinates:
                subtotaalString = extract_text_in_region(name, subtotaal_coordinates)

            if bezoldigingsmaximum_coordinates:
                bezoldigingsmaximumString = extract_text_in_region(name, bezoldigingsmaximum_coordinates)

            if onverschuldigd_coordinates:
                onverschuldigdString = extract_text_in_region(name, onverschuldigd_coordinates)

            if overschrijding_coordinates:
                overschrijdingString = extract_text_in_region(name, overschrijding_coordinates)

            if toelichting_coordinates:
                toelichtingString = extract_text_in_region(name, toelichting_coordinates)

            result_list.append((name, text_in_region, functionString,
                                    functievervullingString, dienstverbandString,dienstbetrekkingString, beloningString,
                                    beloningenString, subtotaalString, bezoldigingsmaximumString,
                                    onverschuldigdString, overschrijdingString,
                                    toelichtingString))  
            
        else:
            print(f"{name} not found on page {target_page + 1}")

    pdf_document.close()
    return result_list

