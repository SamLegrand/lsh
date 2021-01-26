import pandas as pd
from processing import to_shingles
from utils import compute_jaccard, pairwise_jaccard
import random
from multiprocessing import Pool
from usersettings import usersettings
import functools
import matplotlib.pyplot as plt


# Base class for hash functions, just has a calculate(value) method to be overridden
class Basehash:
    def __init__(self):
        pass

    def calculate(self, value):
        raise NotImplementedError


# gives worse results, should not be used :/
class Xorhash(Basehash):
    def __init__(self):
        Basehash.__init__(self)
        self.xor = random.randint(0, 2**64)

    def calculate(self, value):
        return value ^ self.xor


# linear congruential generator-ish (a*x + b) % c
class Linconhash(Basehash):
    def __init__(self):
        Basehash.__init__(self)
        self.a = random.randint(2**32, 2**64) # shouldn't be too small
        self.b = random.randint(0, 2**64)
        self.c = 40420574619972389053  # random large prime


    def calculate(self, value):
        return (self.a*value + self.b) % self.c


# takes a set of shingles and a list of k hash functions, returns a signature of length k
# using minhash
def shingles_to_signature(shingleset, hashfunctions):
    out = []
    for hashfunc in hashfunctions:
        lowest = min({hashfunc.calculate(shingle) for shingle in shingleset})
        out.append(lowest)
    return out


# given a list of shinglesets, returns a new list of signatures
# parameter n determines the amount of hashes being used -> the size of the signatures
def generate_signature_matrix(docs, n):
    assert type(docs) == list

    # generate n new hash functions
    hashfunctions = [Linconhash() for _ in range(n)]

    # calculate signatures for each document
    partialfunc = functools.partial(shingles_to_signature, hashfunctions=hashfunctions)
    with Pool(usersettings["threads"]) as p:
        out = p.map(partialfunc, docs)

    return out


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
    docs = [{1, 2, 3, 4}, {1, 2, 3, 5}, {4, 8, 9, 10}]

    processed = generate_signature_matrix(docs, 10000)  # large signatures of 10000 values

    print("Jaccard:")
    print("jac(0, 1):", compute_jaccard(docs[0], docs[1]))
    print("jac(1, 2):", compute_jaccard(docs[2], docs[1]))
    print("jac(0, 2):", compute_jaccard(docs[2], docs[0]))

    print("")
    print("Using signatures:")
    print("sim(0, 1):", signature_similarity(processed[0], processed[1]))
    print("sim(1, 2):", signature_similarity(processed[2], processed[1]))
    print("sim(0, 2):", signature_similarity(processed[0], processed[2]))


if __name__ == "__main__":
    articles = pd.read_csv('./data/news_articles_small.csv')
    articles['article'] = articles['article'].apply(to_shingles)
    articles = articles.set_index('News_ID').to_dict()['article']

    doclist = list(articles.values())
    print(len(doclist), "docs")

    siglist = generate_signature_matrix(doclist, 100)

    # generate same similarity graph as in sim_analysis.py but using the signatures
    # this isn't faster but just to show that it does work and the similarity using the signatures
    # ~ jaccard index
    buckets = {i / 10: 0 for i in range(0, 10)}

    for i in range(len(siglist)):
        for j in range(len(siglist)):
            if i < j:
                jaccard_sim = signature_similarity(siglist[i], siglist[j])
                buckets[min(jaccard_sim // 0.1 * 0.1, 0.9)] += 1

    lists = buckets.items()
    x, y = zip(*lists)
    # y = [math.log(value) if value != 0 else 0 for value in y]
    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, y)
    plt.xticks(x_pos, x)
    plt.yscale("log")
    plt.show()
