import gzip 
import Levenshtein

def jointy_compress(*elem:str) -> bytes:
    """
    takes in N strings concatenates them together and 
    compresses them with gzip
    """
    string = " ".join(elem) #join with space seperator
    return gzip.compress(bytes(string,encoding="utf-8"))



"""
try using Levenshtein distance for pruning
https://maxbachmann.github.io/Levenshtein/
pip install levenshtein
"""

A ="test test test"
B = "lol lol lol lol test test lol lol lol  test test"
dist = Levenshtein.distance(A,B)

mb = Levenshtein.matching_blocks(Levenshtein.editops(A, B),A,B)
print(mb)

for alignment in mb:
    print(A[:alignment.a] +"["+ A[alignment.a:alignment.a+alignment.size] + "]" + A[alignment.a+alignment.size:])
    print(B[:alignment.b] +"["+ B[alignment.b:alignment.b+alignment.size] + "]" + B[alignment.b+alignment.size:] +"\n")