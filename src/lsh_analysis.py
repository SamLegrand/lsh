from lsh import LSH
import time

if __name__ == "__main__":
    # determine index creation time, specificity and sensitivity for different similarity thresholds
    for M in [20, 50, 100]:
            for r in [2, 4, 5, 10]:
                
                lsh = LSH()
                t = time.time()
                lsh.create_index('news_articles_small.csv', M, r)
                print('Creating index with M=%s, r=%s took' % (M, r), time.time() - t, 'seconds')
                s1 = 0.3
                for s2 in [0.7, 0.8, 0.9]:
                    p1, p2 = lsh.compute_sensitivity(s1, s2)
                    print("The index is (%s, %s, %s, %s)-sensitive" % (s1, p1, s2, p2))
    
    # determine for optimal parameters
    lsh = LSH()
    t = time.time()
    lsh.create_index('news_articles_small.csv', 96, 6)
    print('Creating index with M=%s, r=%s took' % (96, 6), time.time() - t, 'seconds')
    s1 = 0.3
    s2 = 0.8
    p1, p2 = lsh.compute_sensitivity(s1, s2)
    print("The index is (%s, %s, %s, %s)-sensitive" % (s1, p1, s2, p2))
