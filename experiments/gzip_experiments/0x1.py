import gzip 

"""
subset pruning experiment
"""

def jointy_compress(*elem:str) -> bytes:
    """
    takes in N strings concatenates them together and 
    compresses them with gzip
    """
    string = " ".join(elem) #join with space seperator
    return gzip.compress(bytes(string,encoding="utf-8"))
    

A = "test"
B = "test test"
C =  "test test test"

target = "lol lol lol lol test test test lol lol lol "
print("word overlap matters?")
print(len(jointy_compress(A,target))) 
print(len(jointy_compress(B,target)))
print(len(jointy_compress(C,target)))

"""
note that lower overlap can sometimes have a shorter length
"""

print("\nsymetry in the operation?")
print("target+A: ",len(jointy_compress(target,A))," A+target:",len(jointy_compress(A,target))) 
print("target+B: ",len(jointy_compress(target,B))," B+target:",len(jointy_compress(B,target)))
print("target+C: ",len(jointy_compress(target,C))," c+target:",len(jointy_compress(C,target)))

"""
note that the operation is not symetrical
"""