import pandas as pd


def to_shingles(doc, k=3):
    shingles = []
    doc = doc.split()
    for i in range (0,len(doc)-k+1):
        shingles.append(hash(tuple(doc[i:i+k])))
    return shingles
