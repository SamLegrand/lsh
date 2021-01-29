import json
import time
from collections import defaultdict
from functools import partial
from hashlib import md5

import pandas as pd

from jaccard import compute_jaccard
from processing import to_shingles
from signature import (Linconhash, generate_signature_matrix, load_hash,
                       shingles_to_signature)

# Class which takes care of creating an index and allows to search given a query
# or to find all near-duplicate pairs
class LSH():
    # Constructor: a filename of a previously created index may be passed to load it
    # if no filename is passed, an empty index is created
    def __init__(self, filename=None) -> None:
        self.docs = []
        self.index = None
        self.M = None
        self.r = None
        self.hashfunctions = None
        self._filter = partial(to_shingles, stopword_start=True,
                               filter_punctuation=True, remove_capitalization=True) # define pre-processing techniques to be used while generating shingles
        if filename:
            self.load_index(filename)

    # Loads a previously created index
    # Parameters:
    # - filename        name of a previously created index file
    def load_index(self, filename):
        with open('./data/%s' % filename, 'r') as index_file:
            index_dict = json.load(index_file)
            self.M = index_dict['M']
            self.r = index_dict['r']
            self.index = index_dict['index']
            self.docs = [set(doc) for doc in index_dict['docs']]
            self.hashfunctions = [load_hash(hashfunc)
                                  for hashfunc in index_dict['hashfunctions']]

    # Stores the created index into a JSON file
    # Parameters:
    # - filename        name of the index file to be created
    def store_index(self, filename):
        with open('./data/%s' % filename, 'w') as output:
            index_dict = {
                'M': self.M,
                'r': self.r,
                'index': self.index,
                'docs': [list(doc) for doc in self.docs],
                'hashfunctions': [hashfunc.store() for hashfunc in self.hashfunctions]
            }
            json.dump(index_dict, output)

    # Creates an index of a collection given a csv file containing the documents
    # Parameters:
    # - filename        name of the csv file containing the documents
    # - M               length of each signature
    # - r               minhashes per band
    # - hashtype        either "Xorhash" or "Linconhash" or "MD5hash", determines the Minhash algorithm. default: Xorhash
    # n must be a multiple of r.
    def create_index(self, filename, M, r, hashtype="Xorhash"):
        # assert M % r == 0
        articles = pd.read_csv('./data/%s' % filename)
        articles['article'] = articles['article'].apply(self._filter)
        doclist = articles.set_index('News_ID')['article'].to_list()
        self.docs = doclist
        # print(len(doclist), "docs")

        siglist, self.hashfunctions = generate_signature_matrix(doclist, M, hashtype)
        self.r = r
        self.M = M
        self.index = self.index_gen(siglist)

    # Compute (s1, p1, s2, p2)-sensitivity of the index, given s1 and s2
    # Parameters:
    # - s1              lower bound selectivity of tolerance zone
    # - s2              upper bound selectivity of tolerance zone
    # Returns:
    # - a (s1, p1, s2, p2) tuple
    def compute_sensitivity(self, s1, s2):
        if self.index is None:
            print('An index must be created/loaded before computing sensitivity.')
            return None
        return pow(1-pow(s1, self.r), self.M//self.r), 1-pow(1-pow(s2, self.r), self.M//self.r)

    # Find documents with a similarity to the given query larger than sim
    # Parameters:
    # - query           input query for which near-duplicates should be searched
    # - sim             minimum similarity value
    # Returns:
    # - a list of document IDs that have a Jaccard index to the query larger than the given similarity
    def query(self, query, sim):
        results = []
        if self.index is None:
            print('An index must be created/loaded before querying.')
            return results
        # first convert to 3-shingles (includes pre-processing), then convert to minhash signature
        shingles = self._filter(query)
        signature = shingles_to_signature(shingles, self.hashfunctions)

        # candidates = union of candidates per band
        candidates = set()
        for i in range(0, len(signature) // self.r):
            # find candidates for this band
            h = self.hash_band(signature, self.r * i)
            if h not in self.index[i].keys():
                continue
            for band_candidate in self.index[i][h]:
                candidates.add(band_candidate)

        for candidate in candidates:
            # check actual near-duplicate for each candidate
            if compute_jaccard(shingles, self.docs[candidate]) > sim:
                results.append(candidate)

        return results

    # Hash a band of a signature: i denotes the starting index of the band
    # Parameters:
    # - sig             the full signature
    # - i               starting index of the band
    # Returns:
    # - an MD5 hash of this band as a 32-character hexadecimal string
    def hash_band(self, sig, i):
        m = md5()
        for value in tuple(sig[i:i+self.r]):
            m.update(value.to_bytes(8, 'big', signed=False))
        return m.hexdigest()

    # Creates an index with populated buckets given the signature matrix
    # Parameters:
    # - siglist         list of columns in the signature matrix
    # Returns:
    # - the generated buckets as a list of dictionaries, where the index into
    #   the first list is the band number, and the key into the dictionary is
    #   the hash of the band. the buckets are a list
    def index_gen(self, siglist):
        index = [defaultdict(list) for _ in range(self.M // self.r)]
        doc_id = 0
        lim = self.M // self.r * self.r
        for doc in siglist:
            for i in range(0, lim, self.r):
                index[i // self.r][self.hash_band(doc, i)].append(doc_id)
            doc_id += 1
        return index

    # Returns all near-duplicate pairs with a similarity above the given threshold
    # This function also writes the document IDs into a file result.csv
    # Parameters:
    # - treshold        minimum similarity for near-duplicates
    # Returns:
    # - list of all candidate pairs and the Jaccard index [((doc1, doc2), sim), ...]
    def get_all_similar_pairs(self, treshold):
        # 1) loop over all buckets & find pairs (i, j) with i < j (so we don't do (i, j) and (j, i))
        candidates = set()
        for i in range(0, self.M // self.r):
            for bucket in self.index[i].values():
                for j in bucket:
                    for k in bucket:
                        if j < k:
                            candidates.add((j, k))

        print("Found", len(candidates), "candidate pairs")

        # 2) calculate the Jaccard index on the shingles of these documents and only
        #    keep the pairs that are actually similar
        results = set()
        doc_ids1 = []
        doc_ids2 = []
        for pair in candidates:
            sim = compute_jaccard(self.docs[pair[0]], self.docs[pair[1]])
            if sim > treshold:
                doc_ids1.append(pair[0])
                doc_ids2.append(pair[1])
                results.add((pair, sim))

        print("Found", len(results), "near-duplicate pairs")

        # write similar pairs to output csv
        results_csv = pd.DataFrame({'doc_id1': doc_ids1, 'doc_id2': doc_ids2})
        results_csv.sort_values(["doc_id1", "doc_id2"], inplace=True)
        results_csv.to_csv('result.csv', index=False)

        return results


if __name__ == "__main__":
    lsh = LSH()

    t = time.time()
    lsh.create_index('news_articles_large.csv', 100, 5, "Xorhash")
    print("Creating index took", time.time() - t, "sec")
    s1 = 0.3
    s2 = 0.8
    p1, p2 = lsh.compute_sensitivity(s1, s2)
    print("The index is (%s, %s, %s, %s)-sensitive" % (s1, p1, s2, p2))

    t = time.time()
    lsh.store_index('index_5.json')
    print("Storing index took", time.time() - t, "sec")

    t = time.time()
    lsh2 = LSH('index_5.json')
    print("Loading index took", time.time() - t, "sec")

    t = time.time()
    query = "The peseta nosedived to a new all-time low early Friday afternoon on the London forex market, hitting 93.30 to the German mark, Dresdner Bank analyst Elizabeth Legge said. Your work computer just suffered a major meltdown. Maybe the operating system failed, or a virus crashed the hard drive. News that banking giant Goldman Sachs has been charged with fraud sent Asian stocks tumbling Monday, while airlines were hit as northern European airspace was closed due to the Icelandic volcano. Stating that the ``foundation for economic expansion'' has been laid but that the strength and sustainability of the recovery is still uncertain, Alan Greenspan, the Federal Reserve's chairman, strongly suggested to Congress on Wednesday that monetary policy would remain unchanged for the foreseeable Prime Minister Ariel Sharon has told US officials there is no question of freezing Israel's planned expansion of Maale Adumim, the largest Jewish settlement in the West Bank, an aide said Thursday. er, darlings -- are back where they ought to be, make sure you keep an eye on their training for fall sports. The last thing you want is to have them injured and lounging on the couch where they have spent the past three months hollering for food. The heads of the West Coast chapter of the Hollywood performer unions have submitted a tentative contract settlement for a vote by the guilds' nearly 135,000 members. Overseas direct investment in China during the first 10 months this year increased 37 percent in contractual volume from the same period last year."
    plagiarised_docs = lsh2.query(query, 0.8)
    print("Searching query took", time.time() - t, "sec")

    print(plagiarised_docs)
    print("")

    t = time.time()
    print(lsh2.get_all_similar_pairs(0.8))
    print("Retrieving all near-duplicate pairs took", time.time() - t, "sec")
