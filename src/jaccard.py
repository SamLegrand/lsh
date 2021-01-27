
# computes Jaccard similarity based on two documents represented as sets of shingles
def compute_jaccard(doc1, doc2):
    intersection = doc1.intersection(doc2)
    union = doc1.union(doc2)
    return len(intersection)/len(union)

# computes Jaccard similarity between each document pair
def pairwise_jaccard(docs, buckets):
    for key1, value1 in docs.items():
        for key2, value2 in docs.items():
            if key1 < key2:
                jaccard_sim = compute_jaccard(value1, value2)
                # increase bucket count for range in which computed similarity falls
                buckets[min(jaccard_sim // 0.1 * 0.1, 0.9)] += 1
