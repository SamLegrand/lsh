from hashlib import md5
from os import name
from collections import defaultdict
import redis
import pandas as pd
from signature import generate_signature_matrix
from processing import to_shingles
import json

def create_index(signature_matrix, r):
    index = defaultdict(list)
    doc_id = 0
    for doc in signature_matrix:
        for i in range(0, len(doc)-1, r):
            m = md5()
            for value in tuple(doc[i:i+r]):
                m.update(value.to_bytes(8, 'big', signed=True))
            # redis_client.lpush(m.digest(), doc_id)
            index[m.hexdigest()].append(doc_id)
        doc_id += 1
    with open('./data/index.json', 'w') as output:
        json.dump(index, output)


if __name__ == "__main__":
    articles = pd.read_csv('./data/news_articles_small.csv')
    articles['article'] = articles['article'].apply(to_shingles)
    articles = articles.set_index('News_ID').to_dict()['article']

    doclist = list(articles.values())
    print(len(doclist), "docs")

    siglist = generate_signature_matrix(doclist, 100)

    create_index(siglist, 5)
