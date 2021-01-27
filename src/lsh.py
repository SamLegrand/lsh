from hashlib import md5
from collections import defaultdict
import pandas as pd
from signature import generate_signature_matrix, shingles_to_signature, Linconhash
from processing import to_shingles
from jaccard import compute_jaccard
import json

class LSH():
    def __init__(self, filename=None) -> None:
        self.docs = []
        self.index = None
        self.n = None
        self.r = None
        if filename:
            self.load_index(filename)

    def load_index(self, filename):
        with open('./data/%s' % filename, 'r') as index_file:
            index_dict = json.load(index_file)
            self.n = index_dict['n']
            self.r = index_dict['r']
            self.index = index_dict['index']
            self.docs = [set(doc) for doc in index_dict['docs']]

    def store_index(self, filename):
        with open('./data/%s' % filename, 'w') as output:
            index_dict = {'n': self.n, 'r': self.r, 'index': self.index, 'docs': [list(doc) for doc in self.docs]}
            json.dump(index_dict, output)

    def create_index(self, filename, n, r):
        articles = pd.read_csv('./data/%s' % filename)
        articles['article'] = articles['article'].apply(to_shingles)
        doclist = articles.set_index('News_ID')['article'].to_list()
        self.docs = doclist
        print(len(doclist), "docs")

        siglist = generate_signature_matrix(doclist, n)
        self.r = r
        self.n = n
        self.index = self.index_gen(siglist)

    def query(self, query, sim):
        results = []
        if self.index is None:
            print('An index must be created/loaded before querying.')
            return results
        shingles = to_shingles(query)
        signature = shingles_to_signature(shingles, [Linconhash() for _ in range(self.n)])
        candidates = {candidate for i in range(0, len(signature), self.r) for candidate in self.index[self.hash_band(signature, i)]}
        for candidate in candidates:
            if compute_jaccard(shingles, self.docs[candidate]) > sim:
                results.append(candidate)
        return results

    def hash_band(self, sig, i):
        m = md5()
        for value in tuple(sig[i:i+self.r]):
            m.update(value.to_bytes(8, 'big', signed=True))
        return m.hexdigest()

    def index_gen(self, siglist):
        index = defaultdict(list)
        doc_id = 0
        for doc in siglist:
            for i in range(0, len(doc), self.r):
                index[self.hash_band(doc, i)].append(doc_id)
            doc_id += 1
        return index


if __name__ == "__main__":
    lsh = LSH()
    lsh.create_index('news_articles_small.csv', 100, 5)
    lsh.store_index('index_5.json')
    lsh2 = LSH('index_5.json')
    plagiarised_docs = lsh2.query("The peseta nosedived to a new all-time low early Friday afternoon on the London forex market, hitting 93.30 to the German mark, Dresdner Bank analyst Elizabeth Legge said. Your work computer just suffered a major meltdown. Maybe the operating system failed, or a virus crashed the hard drive. News that banking giant Goldman Sachs has been charged with fraud sent Asian stocks tumbling Monday, while airlines were hit as northern European airspace was closed due to the Icelandic volcano. Stating that the ``foundation for economic expansion'' has been laid but that the strength and sustainability of the recovery is still uncertain, Alan Greenspan, the Federal Reserve's chairman, strongly suggested to Congress on Wednesday that monetary policy would remain unchanged for the foreseeable Prime Minister Ariel Sharon has told US officials there is no question of freezing Israel's planned expansion of Maale Adumim, the largest Jewish settlement in the West Bank, an aide said Thursday. er, darlings -- are back where they ought to be, make sure you keep an eye on their training for fall sports. The last thing you want is to have them injured and lounging on the couch where they have spent the past three months hollering for food. The heads of the West Coast chapter of the Hollywood performer unions have submitted a tentative contract settlement for a vote by the guilds' nearly 135,000 members. Overseas direct investment in China during the first 10 months this year increased 37 percent in contractual volume from the same period last year.", 0.8)
    print(plagiarised_docs)
