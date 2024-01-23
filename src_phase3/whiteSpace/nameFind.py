import csv
import fitz

class KeywordFinder:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def find_keywords_with_context(self, page_number, context_width=15, context_height=15):
        keywords = ["Bestuurder", "Voorzitter", "lid","Secretaris","Directeur"]
        unique_names = set()
        results = []
        page = self.doc[page_number-1]## page number starts from 1
        words = page.get_text("words")

        for keyword in keywords:
            for i, word_info in enumerate(words):
                word_text = word_info[4]
                if keyword.lower() in word_text.lower():
                    # Calculate coordinates for the region above the keyword
                    x0_kw, y0_kw, x1_kw, y1_kw = word_info[:4]
                    above_region = (max(0, x0_kw - context_width), max(0, y0_kw - context_height), x1_kw, y0_kw)

                    # Get the text in the above region
                    above_text = self.get_text_in_region(page, above_region)

                    # Check if the name is unique before adding it to results
                    if above_text not in unique_names:
                        unique_names.add(above_text)
                        results.append(
                            #'FileName': self.pdf_path,
                            #'keyword': keyword,
                            above_text
                            #'Pagenumber': page_number  # Page numbers start from 1
                        )
        return results

    def get_text_in_region(self, page, region):
        # Extract text in the specified region
        text = page.get_text("text", clip=region)
        return text.strip()

    def close(self):
        self.doc.close()

# Example usage
def main():
    # Read input from CSV file
    csv_file_path = "test2.csv"
    output_csv_path = "namesFinder.csv"

    # with open(csv_file_path, newline='') as csvfile:
    #     reader = csv.DictReader(csvfile)

    #     for row in reader:
    #         pdf_path = row['FileName']
    #         page_number_to_search = int(row['Pagenumber'])
    #         keywords_to_find = ["Bestuurder", "Voorzitter", "lid","Secretaris","Directeur"]
    #         pdf_path = f"pdfs/{pdf_path}.pdf"

    #         keyword_finder = KeywordFinder(pdf_path)
    #         result = keyword_finder.find_keywords_with_context(keywords_to_find, page_number_to_search, context_width=15, context_height=15)
    #         keyword_finder.close()

    #         # Append results to the CSV file with column titles for each row
    #         with open(output_csv_path, mode='a', newline='') as output_csv:
    #             fieldnames = ['FileName', 'keyword', 'Name', 'Pagenumber']
    #             writer = csv.DictWriter(output_csv, fieldnames=fieldnames)

    #             # Write column titles for each row
    #             if output_csv.tell() == 0:
    #                 writer.writeheader()

    #             writer.writerows(result)
    #         print(result)

if __name__ == "__main__":
    main()
