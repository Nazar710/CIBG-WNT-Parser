import PyPDF2
import spacy
import numpy as np 


class free_text():
    def __init__(self,download_spacy:bool=True,nlp_core_path:str="nl_core_news_sm") -> None:
        if(download_spacy):
            spacy.cli.download(nlp_core_path)
        self.NER = spacy.load(nlp_core_path)

    def extract_named_entities(self,text:str) -> list[tuple[str,str]]:
        doc = self.NER(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def entity_replacer(self,text:str) -> str:
        """
        replaces all the words in the text with their found entity type.

        return the string with all it's enities replaced by their entity type
        """
        ents = self.NER(text).ents  

        mask = np.ones(len(text))
        labels = []
        for ent in ents:
            mask[ent.start_char:ent.end_char] = 0
            labels.append(ent.label_)

        current_num = 1 
        current_label_index = 0
        new_text = ""
        for text_pos,num in enumerate(mask):
            if(num < current_num):
                new_text += "["+labels[current_label_index]+"]"
                current_label_index += 1
            
            if(num == 1):
                new_text += text[text_pos]
            current_num = num 

        return new_text

    def find_sentences_with_keywords_and_entities(self,text:str, keywords:list[str],use_entities:bool=True)->list[str]:

        # Convert text and keywords to lowercase for case-insensitive comparison
        keywords_lower = [keyword.lower() for keyword in keywords] #TODO lowering here will break name/person detection as it heavilly relies on capitalization
        #TODO fix the bug that lowering breaks the person names. (first finding person names than replacing it with NER, then lower and try to detect the rest)
        #as sometimes not lowering will break it (for dates).

        if(use_entities):
            text = self.entity_replacer(text)
            keywords_lower = [self.entity_replacer(keywords_lower) for keywords_lower in keywords_lower]
        print(keywords_lower)

        sentences = [sentence.text.strip() for sentence in self.NER(text).sents if
                    any(keyword in sentence.text.lower() for keyword in keywords_lower)]

        return sentences

    @staticmethod   
    def save_sentences_to_file(sentences, output_file):
        with open(output_file, 'w', encoding='utf-8') as file:
            for sentence in sentences:
                file.write(sentence + '.\n')

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text

if __name__ == "__main__":
    pdf_path = "testTables.pdf"
    output_file = "output_sentences_with_keywords_and_entities.txt"

    free_text_obj = free_text(download_spacy=False)

    extracted_text = free_text_obj.extract_text_from_pdf(pdf_path)

    # Define your keywords
    keywords = ["bezoldiging 2020"]

    # Find sentences containing the keywords in a case-insensitive manner, along with entities
    sentences_with_keywords_and_entities = free_text_obj.find_sentences_with_keywords_and_entities(extracted_text, keywords,use_entities=True)
    # Save the sentences containing keywords and entities to a text file
    free_text_obj.save_sentences_to_file(sentences_with_keywords_and_entities, output_file)
