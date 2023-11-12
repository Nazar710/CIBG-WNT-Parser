import spacy
import string 
import numpy as np  
    
# spacy.cli.download("en_core_web_sm")
# NER = spacy.load("en_core_web_sm")
# spacy.cli.download("nl_core_news_sm")
NER = spacy.load("nl_core_news_sm")

def spacy_large_ner(document):
  return {(ent.text.strip(), ent.label_) for ent in NER(document).ents}

print("English: ",spacy_large_ner("Lisa was walking down the street and saw a €5 bill and a 10, 20 and 30 on the ground in Berlin. "))
print("Dutch: ",spacy_large_ner("lisa liep door de straat en zag een €5 bill en een 10, 20 en 30 op de grond in Berlijn."))



def entity_replacer(text:str) -> tuple[str,str]:
    ents = NER(text).ents  

    mask = np.ones(len(text))
    labels = []
    for ent in ents:
        print("position_selected_ent: ",text[ent.start_char:ent.end_char])
        print("LABEL: ", ent.label_)

        mask[ent.start_char:ent.end_char] = 0
        labels.append(ent.label_)

    current_num = 1 
    current_label_index = 0
    new_text = ""
    for text_pos,num in enumerate(mask):
        if(num < current_num):
            new_text += labels[current_label_index]
            current_label_index += 1
        
        if(num == 1):
            new_text += text[text_pos]
        current_num = num 

    return new_text,text
    
text = "lisa liep door de straat en zag een €5 bill en een 10, 20 en 30 op de grond in Berlijn..."

new_text,text = entity_replacer(text)
print(text)
print(new_text)