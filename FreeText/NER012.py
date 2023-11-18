import PyPDF2
import spacy


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text


def extract_named_entities(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities


def find_sentences_with_keywords_and_entities(text, keywords):
    nlp = spacy.load("en_core_web_sm")

    # Convert text and keywords to lowercase for case-insensitive comparison
    text_lower = text.lower()
    keywords_lower = [keyword.lower() for keyword in keywords]

    sentences = [sentence.text.strip() for sentence in nlp(text).sents if
                 any(keyword in sentence.text.lower() for keyword in keywords_lower)]
    return sentences


def save_sentences_to_file(sentences, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for sentence in sentences:
            file.write(sentence + '.\n')


pdf_path = "testTables.pdf"
output_file = "output_sentences_with_keywords_and_entities.txt"

extracted_text = extract_text_from_pdf(pdf_path)

# Define your keywords
keywords = ['leidinggevende', 'bezoldiging', 'bezoldigingsmaximum', 'functie', 'dienst', 'topfunctionaris',
            'onkostenvergoeding', 'individueel', 'WNT']

# Find sentences containing the keywords in a case-insensitive manner, along with entities
sentences_with_keywords_and_entities = find_sentences_with_keywords_and_entities(extracted_text, keywords)

# Save the sentences containing keywords and entities to a text file
save_sentences_to_file(sentences_with_keywords_and_entities, output_file)
