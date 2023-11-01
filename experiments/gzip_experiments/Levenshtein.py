import gzip 
import Levenshtein

"""
(Sander Stokhof)

using levenshtein to align subset of a text with the matching subset of the text.
where the subset is being isolated with brackets. 

"""





"""
try using Levenshtein distance for pruning
https://maxbachmann.github.io/Levenshtein/
pip install levenshtein
"""

# A ="test test test"
# B = "lol lol lol lol test test lol lol lol  test test"


A ="test test hello"
B = "lol lol lol lol test test lol lol lol"
dist = Levenshtein.distance(A,B)

mb = Levenshtein.matching_blocks(Levenshtein.editops(A, B),A,B)
print(mb)

for alignment in mb:
    print(A[:alignment.a] +"["+ A[alignment.a:alignment.a+alignment.size] + "]" + A[alignment.a+alignment.size:])
    print(B[:alignment.b] +"["+ B[alignment.b:alignment.b+alignment.size] + "]" + B[alignment.b+alignment.size:] +"\n")