import csv
import fitz

class KeywordFinder:
    """Looks for keywords that might appear after function, infers name from the location above
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def find_keywords_with_context(self, page_number: int, context_width:float=15, context_height:float=15) -> list:
        keywords = ["Bestuurder", "Voorzitter", "lid","Secretaris","Directeur"]
        unique_names = set()
        results = []
        page = self.doc[page_number-1] ## page number starts from 1
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

    def get_text_in_region(self, page: int, region: any) -> tuple[str, list, dict]:
        # Extract text in the specified region
        text = page.get_text("text", clip=region)
        return text.strip()

    def close(self):
        self.doc.close()

