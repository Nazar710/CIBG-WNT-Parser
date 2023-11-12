import spacy
from spacy import displacy

# spacy.cli.download("en_core_web_sm")
# NER = spacy.load("en_core_web_sm")
# spacy.cli.download("nl_core_news_sm")
NER = spacy.load("nl_core_news_sm")

def spacy_large_ner(document):
  return {(ent.text.strip(), ent.label_) for ent in NER(document).ents}

print("English: ",spacy_large_ner("Lisa was walking down the street and saw a €5 bill and a 10, 20 and 30 on the ground in Berlin. "))
print("Dutch: ",spacy_large_ner("lisa liep door de straat en zag een €5 bill en een 10, 20 en 30 op de grond in Berlijn."))