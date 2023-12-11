import requests
from bs4 import BeautifulSoup
import string
from tqdm import tqdm     
import pandas as pd 
from time import sleep

def extract_page(url:str):
    """
    to fix problems with browser user-agent
    """
    headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
    page =requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup



if __name__ == "__main__":
    letters = [i for i in string.ascii_lowercase]
    root_url = "http://www.telefoonboek.nl/zoeken-op-naam/"

    all_names = set({})

    for letter in tqdm(letters,ascii=True):
        for i in range(30):
            sleep(1) #as no one wants to get rate limited 
            url = root_url + letter +"/" +"pagina"+str(i+1)+"/" #we can naively do this as their website sets to first page is pagina0 or pagina1. pagina8 is pagina6 if there are only 6 pages. 
            print(url)
            soup = extract_page(url)
            names = [elem.get_text() for elem in soup.find_all("ul", class_="contentbox__lists--columns2-split")[0].find_all("li")] 

            before_length = len(all_names)
            all_names = all_names.union(set(names))

            if(not (before_length < len(all_names))):
                #since they start repeating pages when the page you look for is too high
                break


    df = pd.DataFrame(all_names)
    df.to_csv("phonebook.csv")