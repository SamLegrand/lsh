import pandas as pd
import binascii

# combine two CRC32s to create a 64-bit result (no built-in CRC64 but this should suffice)
def longcrc(shingle):
    bytestr = str.encode(" ".join(shingle))
    shingle.reverse()
    bytestr2 = str.encode(" ".join(shingle))
    lower = binascii.crc32(bytestr) % (1 << 32)
    upper = binascii.crc32(bytestr2) % (1 << 32)
    return lower | (upper << 32)

# turns a document into a set of hashed shingles
def to_shingles(doc, k=3):
    shingles = set()
    doc = doc.split()
    for i in range (0,len(doc)-k+1):
        #shingles.add(hash(tuple(doc[i:i+k])))
        shingles.add(longcrc(doc[i:i+k]))
    return shingles
