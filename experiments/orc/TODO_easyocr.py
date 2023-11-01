import easyocr
from PIL import Image

"""
(Sander Stokhof)
(zijiandongkurt )
https://github.com/JaidedAI/EasyOCR

using easyocr to do ocr
"""



import easyocr

# Initialize the EasyOCR reader with the desired language(s)
reader = easyocr.Reader(['en'])  # You can specify multiple languages if needed

# Load an image for OCR
image_path = '1.png'

# Perform OCR on the image
results = reader.readtext(image_path)

# Print the OCR results
for (bbox, text, prob) in results:
    print(f'Text: {text}, Probability: {prob}')


#TODO try to extract tables
