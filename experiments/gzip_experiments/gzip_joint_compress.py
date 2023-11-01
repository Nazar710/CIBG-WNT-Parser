import gzip 

"""
(Sander Stokhof)
arXiv: "Less is More: Parameter-Free Text Classification with Gzip"

subset pruning experiment.

Jointly compress sentences together with gzip to see how the length of the compression behave for different overlaps.
Where we looking at differences in joint compression lengths of different words
and if length extension changes things
"""
a = "test"
b = "hello"
c = "test test"
d = "lol lol lol"

e = "test lol"
f = "test lol lol" 
g = "test test test"

h = "TEST"


print("test                 :", len(gzip.compress(bytes(a,encoding="utf-8"))))
print("test | test          :", len(gzip.compress(bytes(a+a,encoding="utf-8"))))
print("test | hello         :", len(gzip.compress(bytes(a+b,encoding="utf-8"))))
print("test | lol lol lol   :", len(gzip.compress(bytes(a+d,encoding="utf-8"))))
print("\n")
print("test | test lol      :", len(gzip.compress(bytes(a+e,encoding="utf-8"))))
print("test | test lol lol  :", len(gzip.compress(bytes(a+f,encoding="utf-8"))))
print("test | test test test:",len(gzip.compress(bytes(a+g,encoding="utf-8"))))
print("\n")
print("test | TEST          :",len(gzip.compress(bytes(a+h,encoding="utf-8")))) 

"""
is case sensitive, is sensitive to size difference (but can reasonably well figure out if it is the same)
since case sensitive 
"""
