import pandas as pd
from processing import to_shingles
from jaccard import compute_jaccard
import random
from multiprocessing import Pool
from usersettings import usersettings
import functools
import matplotlib.pyplot as plt
from hashlib import md5

# Base class for hash functions, just has methods to be overridden
class Basehash:
    # Empty constructor
    def __init__(self):
        pass

    # Function which calculates the hash value of a given input integer
    def calculate(self, value):
        raise NotImplementedError

    # Returns a string which is used to store the hash function
    def store(self):
        raise NotImplementedError


# Takes a string as input as generated by .store() and returns the object
def load_hash(s):
    split = s.split("_")
    assert len(split) > 0
    hashtype = split[0]

    if hashtype == "Xorhash":
        obj = Xorhash()
        obj.xor = int(split[1])
        return obj

    if hashtype == "Linconhash":
        obj = Linconhash()
        obj.a = int(split[1])
        obj.b = int(split[2])
        obj.c = int(split[3])
        return obj

    if hashtype == "MD5hash":
        obj = MD5hash()
        obj.a = int(split[1])
        return obj

    assert False


# Xorhash: returns the input number xored with a randomly chosen integer: almost 2x as fast as Linconhash
class Xorhash(Basehash):
    def __init__(self):
        Basehash.__init__(self)
        self.xor = random.randint(0, 2**64)

    def calculate(self, value):
        return value ^ self.xor

    def store(self):
        return "Xorhash_"+str(self.xor)


# Linear congruential generator-ish: (a*x + b) % c for a random a, b.
# c is chosen as a large prime of around 59 bits: this ensures that the hash value fits in 64 bits
class Linconhash(Basehash):
    def __init__(self):
        Basehash.__init__(self)
        self.a = random.randint(2**32, 2**64) # shouldn't be too small
        self.b = random.randint(0, 2**64)
        self.c = 533603009383305529  # random large prime

    def calculate(self, value):
        return (self.a*value + self.b) % self.c

    def store(self):
        return "Linconhash_"+str(self.a)+"_"+str(self.b)+"_"+str(self.c)


class MD5hash(Basehash):
    def __init__(self):
        Basehash.__init__(self)
        self.a = random.randint(0, 2**64)

    def calculate(self, value):
        m = md5()
        m.update(value.to_bytes(8, 'big', signed=False))
        m.update(self.a.to_bytes(8, 'big', signed=False))
        return int(m.hexdigest()[0:16], 16)

    def store(self):
        return "MD5hash_"+str(self.a)


# takes a set of shingles and a list of k hash functions, returns a signature of length k
# using minhash
def shingles_to_signature(shingleset, hashfunctions):
    out = []
    for hashfunc in hashfunctions:
        lowest = min({hashfunc.calculate(shingle) for shingle in shingleset})
        out.append(lowest)
    return out


# given a list of shinglesets, returns a new list of signatures + the hash functions
# parameter n determines the amount of hashes being used -> the size of the signatures
# parameter hashfunc is a string that should either be "Xorhash" or "Linconhash"
def generate_signature_matrix(docs, n, hashfunc):
    assert type(docs) == list

    hashfunc_map = {
        "Xorhash": Xorhash,
        "Linconhash": Linconhash,
        "MD5hash": MD5hash
    }

    assert hashfunc in hashfunc_map.keys()
    hashfunc = hashfunc_map[hashfunc]

    # generate n new hash functions
    hashfunctions = [hashfunc() for _ in range(n)]

    # calculate signatures for each document
    partialfunc = functools.partial(shingles_to_signature, hashfunctions=hashfunctions)
    with Pool(usersettings["threads"]) as p:
        out = p.map(partialfunc, docs)

    return out, hashfunctions


# calculates the similarity of two signatures by counting in how many positions they are equal
def signature_similarity(sig1, sig2):
    assert type(sig1) == list
    assert type(sig2) == list
    assert len(sig1) == len(sig2)

    count = 0
    for i in range(len(sig1)):
        if sig1[i] == sig2[i]:
            count += 1
    return count / len(sig1)


def example_simple():
    docs = [{1, 2, 3}, {3, 4, 5}, {6}]

    siglist, hashfunctions = generate_signature_matrix(docs, 10000, "MD5hash")  # large signatures of 10000 values

    print("Jaccard:")
    print("jac(0, 1):", compute_jaccard(docs[0], docs[1]))
    print("jac(1, 2):", compute_jaccard(docs[2], docs[1]))
    print("jac(0, 2):", compute_jaccard(docs[2], docs[0]))

    print("")
    print("Using signatures:")
    print("sim(0, 1):", signature_similarity(siglist[0], siglist[1]))
    print("sim(1, 2):", signature_similarity(siglist[2], siglist[1]))
    print("sim(0, 2):", signature_similarity(siglist[0], siglist[2]))


if __name__ == "__main__":
    example_simple()
