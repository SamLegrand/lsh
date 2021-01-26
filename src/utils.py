
# Computes Jaccard similarity based on two documents represented as sets of shingles
def compute_jaccard(doc1, doc2):
    intersection = doc1.intersection(doc2)
    union = doc1.union(doc2)
    return len(intersection)/len(union)

# Compute Jaccard similarity with all other articles for a given article
def pairwise_jaccard(article, articles, buckets):
    for key, value in articles.items():
        if article[0] != key:
            jaccard_sim = compute_jaccard(article[1], value)
            buckets[jaccard_sim // 0.1 * 0.1] += 1
