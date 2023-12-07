import re
import spacy

### Note: the good thing is, 90% name hase prefix with uppercase-dot (868 out of 964)
#   various titles such as "dr.", "drs.", "Dhr.", "mr.", "mrs.", "De heer", "Mevrouw", "Kolonel", "Envoy", "Kapitein", "Commissioner", and "Lt."
##   issue left: 1. sometimes can't capture whole name; 2.some name doesn't have any prefix
#                  3. set restriction of: only certain area contains name. to avoid false identification
#
#
#
#


class FreeText:
    def __init__(self, download_spacy: bool = False, nlp_core_path: str = "nl_core_news_sm") -> None:
        if download_spacy:
            spacy.cli.download(nlp_core_path)
        self.NER = spacy.load(nlp_core_path)

    def find_names_Regex(self, text: str):
        count = 0;
        result_string = ''
        pattern = re.compile(r'\b(?:[A-Z]\.){1,4}(?=\s*[A-Z])\s*[A-Z][a-z]{0,20}\b')
        pattern2 = re.compile(
            r'(?:dr\.|drs\.|Dhr\.|mr\.|mrs\.|De\sheer|Mevrouw|Kolonel|Envoy|Kapitein|Commissioner|Lt\.) (\S+)')

        lines = text.splitlines()
        for line in lines:
            line_output = ''
            # Rules
            matchs1 = pattern.findall(line)
            matchs2 = pattern2.findall(line)
            doc = self.NER(line)
            NERnames = [ent.text for ent in doc.ents if ent.label_.lower() == "person"]

            combined_names = list(set(matchs1 + matchs2 + NERnames))
            combined_names = list(map(str, combined_names))


            #for item in combined_names:
                #if any(char.isalpha() for char in item) and item not in line_output:
                    #    print("item: ", item)
                    #    line_output += item
                    #   count += 1

            if any(any(char.isalpha() for char in item) for item in matchs1):
                for item1 in list(map(str, matchs1)):
                    line_output += item1
                count += 1
            elif any(any(char.isalpha() for char in item) for item in matchs2):
                for item2 in list(map(str, matchs2)):
                    line_output += item2
                    count += 1
            elif any(any(char.isalpha() for char in item) for item in NERnames):
                for item3 in list(map(str, NERnames)):
                    line_output += item3
                    count += 1
            # Combine above found items, without duplicate.
            result_string += line_output
            result_string += '\n'


        # Print or use result_string as needed
        print("Matches found:", result_string)

        # Save the result to a file
        output_file_name0 = 'all_names_found.txt'
        print("Number of name found: ", count)
        with open(output_file_name0, 'w') as new_file:
            new_file.write(result_string)

        return result_string

    def find_names_NER(self, text: str) -> list[str]:
        doc = self.NER(text)
        NERnames = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        print("matches found:", NERnames)
        output_file_name1 = 'NER_found.txt'

        # Open the new file in write mode
        with open(output_file_name1, 'w') as new_file:
            result_string = '\n'.join(NERnames)
            new_file.write(result_string)
        return NERnames


if __name__ == "__main__":


    test_path = 'nameList.txt'
    with open(test_path, 'r') as file:
        # Read the entire content of the file
        content = file.read()
    # Create an instance of the FreeText class
    free_text_instance = FreeText()

    # Call the find_names method on the instance
    names = free_text_instance.find_names_Regex(content)
    print("Please see the output file called 'all_names_found'")

   # names2 = free_text_instance.find_names_NER(content)
   # print("by NER:", names2)
