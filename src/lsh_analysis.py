from lsh import LSH
import time
import random
import pandas as pd

# determine index creation time, specificity and sensitivity for different similarity thresholds (0.7, 0.8 and 0.9)
def perform_analysis(M, r, queries):
    lsh = LSH()
    t = time.time()
    lsh.create_index('news_articles_small.csv', M, r)
    print('Creating index with M=%s, r=%s took' % (M, r), time.time() - t, 'seconds')
    s1 = 0.3
    for s2 in [0.7, 0.8, 0.9]:
        p1, p2 = lsh.compute_sensitivity(s1, s2)
        print("The index is (%s, %s, %s, %s)-sensitive" % (s1, p1, s2, p2))
        print("Precision for similarity threshold %s:" % s2, test_precision(M, r, s2, queries, 10))

# determine precision on set of queries
# a query is an original document that has been mutated
def test_precision(M, r, sim, queries, iterations):
    precision_values = []
    for i in range(iterations):
        lsh = LSH()
        lsh.create_index('news_articles_small.csv', M, r)
        result_amount = 0
        candidate_amount = 0
        for query in queries:
            results, candidates = lsh.query(query, sim, True)
            result_amount += results
            candidate_amount += candidates
        precision_values.append(result_amount/candidate_amount)

    # return average precision over all iterations
    return sum(precision_values)/iterations

# generates n queries by mutating original documents
def generate_mutated_queries(n):
    mutations = ['random', 'mutation', 'specificity', 'sensitivity', 'precision']
    df = pd.read_csv('./data/news_articles_small.csv')
    queries = df.head(n)['article'].to_list()

    for i in range(len(queries)):
            for mutation in mutations:
                to_replace = random.choice(queries[i].split())
                queries[i] = queries[i].replace(to_replace, mutation, 1)
    return queries


if __name__ == "__main__":
    # use 100 queries for determining precision
    queries = generate_mutated_queries(100)

    # perform analysis for different combinations of signature length M and number of rows per band r
    for M in [20, 50, 100]:
            for r in [2, 4, 5, 10]:
                perform_analysis(M, r, queries)
    
    # determine for optimal parameters
    perform_analysis(96, 6, queries)
