import fitz  # PyMuPDF
import spacy
import pandas as pd
import re  # Import the regular expression module
import pickle
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the Dutch spaCy model
nlp = spacy.load("nl_core_news_sm")

class PDFTextExtractor:
    def __init__(self, pdf_path, page_number=None, word_space_size=4):
        self.pdf_path = pdf_path
        self.page_number = page_number
        self.word_space_size = word_space_size
        self.listwords = ["N.v.t", "N.v.t."]


    def check_combined_pattern(self, text, phonebook_df,extracted_sentences):
        # Check if the text follows the combined pattern
        if self.check_pattern(text):
            #print(text)
            if check_presence_in_phonebook(text, phonebook_df):
                return True

            # Check the next sentence and the one after an empty line
            next_sentence = self.get_next_non_empty_sentence(text,extracted_sentences)
            print(next_sentence)
            if check_presence_in_phonebook(next_sentence, phonebook_df):
                return True, f"{text} {next_sentence}"
                
                
                # second_next_sentence = self.get_next_non_empty_sentence(next_sentence)
                # if second_next_sentence and check_presence_in_phonebook(second_next_sentence, phonebook_df):
                #     # Check if Z x0 is in the same x0 coordinate of X with a range of 5
                #     #if self.is_x0_in_range_of_XZ(text, second_next_sentence, 5):
                #     return True, f"Combine: {text} {second_next_sentence}"

        return False
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False


    def get_next_non_empty_sentence(self, text, extracted_sentences):
            # Get the next non-empty sentence from the extracted sentences
            # (assuming sentences are separated by an empty line)
            sentences = extracted_sentences[extracted_sentences.index(text)+1:]

            for sentence in sentences:
                if sentence and not sentence.isspace():
                    return sentence.strip()
            return None


    def is_x0_in_range_of_XZ(self, text_X, text_Z, range_threshold):
        # Check if Z x0 is in the same x0 coordinate of X with a specified range threshold
        # (Assuming x0 is the left coordinate of the text bounding box)
        inst_X = self.get_text_instance(text_X)
        inst_Z = self.get_text_instance(text_Z)

        if inst_X and inst_Z:
            x0_X, x0_Z = inst_X.x0, inst_Z.x0
            return abs(x0_X - x0_Z) <= range_threshold
        return False

    def get_text_instance(self, text):
        # Get the text instance using the search_for method
        doc = fitz.open(self.pdf_path)
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text_instances = page.search_for(text)
            if text_instances:
                doc.close()
                return text_instances[0]
        doc.close()
        return None

    def extract_sentences(self):
        doc = fitz.open(self.pdf_path)
        sentences = []

        if self.page_number is not None:
            start_page = self.page_number - 1
            end_page = self.page_number
        else:
            start_page = 0
            end_page = doc.page_count

        for page_num in range(start_page, end_page):
            page = doc[page_num]
            text = page.get_text("text")

            lines = text.split('\n')

            for line in lines:
                sentence_start = 0
                word_space = 0

                for i in range(1, len(line)):
                    if line[i] == ' ' and line[i - 1] != ' ':
                        word_space = i - sentence_start
                        if word_space >= self.word_space_size:
                            sentence = line[sentence_start:i]
                            # Check if the sentence is a number or "N.v.t"
                            words = sentence.split()
                            if not any(self.is_number(word) or word.strip() in self.listwords for word in words):
                                sentences.append(' '.join(words))

                            sentence_start = i + 1

                # Add the last part of the line as a sentence
                sentence = line[sentence_start:]
                words = sentence.split()
                if not any(self.is_number(word) or word.strip() in self.listwords for word in words):
                    sentences.append(' '.join(words))

                # Add extra sentence distance check between lines
                sentences.append('')  # Add an empty line to simulate sentence distance

        doc.close()

        return sentences

    def check_pattern(self, text):
        # Check for the specified cases: "A. ", "A.", " .A", ".A", "A.A"
        words = text.split()
        for i, word in enumerate(words):
            if "." in word:
                if i > 0 and (i == len(words) - 1 or words[i + 1].isspace() or words[i + 1] == ""):
                    return True
                elif i < len(words) - 1 and (i == 0 or words[i - 1].isspace() or words[i - 1] == ""):
                    return True
                elif "." in word and "." in word[1:]:
                    return True
        return False

def check_presence_in_phonebook(text, phonebook_df):
    # Check if the text is present in the 'phonebook.csv'
    return text in phonebook_df['Name'].values

def predict_probabilities(names, loaded_model, loaded_tokenizer):
    sequences = loaded_tokenizer.texts_to_sequences(names)
    padded_sequences = pad_sequences(sequences, maxlen=loaded_model.input_shape[1], padding='post')
    predictions = loaded_model.predict(padded_sequences)
    return predictions

def detect_high_probability_names(pdf_path, word_space_size, page_number, model_path, tokenizer_path, probability_threshold=0.90):
    pdf_extractor = PDFTextExtractor(pdf_path, page_number, word_space_size)
    extracted_sentences = pdf_extractor.extract_sentences()
    # Create a DataFrame with the extracted sentences
    
    #df = pd.DataFrame({'Name': extracted_sentences})
    #output_file = 'senetneces.csv'
    #df.to_csv(output_file, index=False, header=False)

    # Create a DataFrame with the extracted sentences
    df_pdf = pd.DataFrame({'Name': extracted_sentences})

    # Load the name detection model and tokenizer
    loaded_model = load_model(model_path)
    with open(tokenizer_path, 'rb') as tokenizer_file:
        loaded_tokenizer = pickle.load(tokenizer_file)

    # Predict probabilities
    predictions = predict_probabilities(df_pdf['Name'].tolist(), loaded_model, loaded_tokenizer)

    # Filter names with probabilities greater than the threshold
    high_prob_df = df_pdf[predictions[:, 0] > probability_threshold]

    return high_prob_df


def merge_keywords_in_range(pdf_path, df, x_range_threshold=20, y_range_threshold=20):
    # Initialize a list to store merged and non-merged keywords
    merged_keywords = []

    # Iterate through the sorted DataFrame
    index = 0
    while index < len(df):
        current_row = df.iloc[index]
        current_text_instance = PDFTextExtractor(pdf_path).get_text_instance(current_row['Name'])
        
        # Check if the text instance is found
        if current_text_instance:
            y0_current, y1_current, x0_current, x1_current = (
                current_text_instance.y0,
                current_text_instance.y1,
                current_text_instance.x0,
                current_text_instance.x1,
            )

            # Initialize a list to store keywords within the same range
            keywords_to_merge = [current_row['Name']]
            current_x_y_pair = (x0_current, y0_current, x1_current, y1_current)

            # Check if the next string is near in Y coordinate and X coordinate
            next_index = index + 1
            while next_index < len(df):
                next_row = df.iloc[next_index]
                next_text_instance = PDFTextExtractor(pdf_path).get_text_instance(next_row['Name'])
                
                # Check if the text instance is found
                if next_text_instance:
                    y0_next, y1_next, x0_next, x1_next = (
                        next_text_instance.y0,
                        next_text_instance.y1,
                        next_text_instance.x0,
                        next_text_instance.x1,
                    )

                    # Check if the Y and X coordinates are within the threshold
                    next_x_y_pair = (x0_next, y0_next, x1_next, y1_next)
                    if (
                        abs(y0_current - y0_next) <= y_range_threshold
                        and abs(y1_current - y1_next) <= y_range_threshold
                        and abs(x0_current - x0_next) <= x_range_threshold
                        and abs(x1_current - x1_next) <= x_range_threshold
                        and current_x_y_pair != next_x_y_pair
                    ):
                        keywords_to_merge.append(next_row['Name'])
                        index = next_index
                        next_index += 1
                    else:
                        break

                else:
                    # Handle the case where next_text_instance is None
                    next_index += 1

            # Add the merged string to the final list
            merged_keywords.append(' '.join(keywords_to_merge))
            index += 1
        else:
            # Handle the case where current_text_instance is None
            index += 1

    merged_keywords = pd.DataFrame({'Name': merged_keywords})

    return merged_keywords





def main():
    # pdf_path = 'pdfs/DigiMV2020_3GH4J7JM3R_0_41208154_Jaarrekening_11833_Leger des Heils Welzijns- en Gezondheidszorg (Stichting).pdf'
    # word_space_size = 500
    # page_number = 110
    # model_path = 'name_detection_model.h5'
    # tokenizer_path = 'tokenizer.pkl'

    # high_prob_df = detect_high_probability_names(pdf_path, word_space_size, page_number, model_path, tokenizer_path)

    # # Merge keywords within the same range
    # merged_df= merge_keywords_in_range(pdf_path,high_prob_df)
    # print(merged_df)


    # # Print or save the DataFrame with high probability names
    # print(high_prob_df)
    print("FINDING NAMES ..........")

if __name__ == "__main__":
    main()
