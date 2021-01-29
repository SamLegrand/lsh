import pandas as pd
from processing import to_shingles
from jaccard import pairwise_jaccard
from functools import partial
import matplotlib.pyplot as plt
import time

# computes probability of sharing a bucket for a given similarity, based on a given signature length M and number of rows per band r
# number of bands b is derived from the number of rows per band (M//r)
def compute_sensitivity(s2, M, r):
    return 1-pow(1-pow(s2, r), M//r)

# plots Jaccard similarity distribution, given a dictionarity of buckets/bins (with counts)
# optionally plots a set of S-curves on top of the distribution
def plot_jaccard_distribution(docs, suffix, plot_sensitivity=False):
    docs = docs.to_dict()['article']
    buckets = {i/10: 0 for i in range(0, 10)}

    # compute Jaccard similarity for each article pair
    pairwise_jaccard(docs, buckets)

    # plot similarity range counts
    lists = buckets.items()
    x, y = zip(*lists)
    x_pos = [i for i, _ in enumerate(x)]
    rects = plt.bar(x_pos, y, align='edge', width=1)
    for rect in rects:
        # add amount in bucket as a label of the bar
        height = rect.get_height()
        plt.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    plt.yscale("log")
    plt.ylabel('Number of document pairs')
    plt.xlabel('Similarity between pairs')

    if plot_sensitivity:
        # plot S-curve on top of similarity distribution for different parameter combinations
        _s = [i/1000 for i in range(0, 1000, 1)]
        colors = ['c', 'm', 'y', 'g']
        axes2 = plt.twinx()
        for M in [20, 50, 100]:
            color = 0
            for r in [2, 4, 5, 10]:
                plt.xticks(x_pos, x)
                _y = [compute_sensitivity(s, M, r) for s in _s]
                axes2.plot([s*10 for s in _s], _y, color=colors[color], label='r = %s' % (r))
                axes2.set_ylim(0, 1)
                # axes2.set_xlim(0, 1)
                axes2.set_ylabel('Probability of sharing a bucket')
                axes2.legend()
                color += 1
            plt.savefig('./plots/s_curve_%s' % (M))
            axes2.clear()

    plt.xticks(x_pos, x)
    plt.savefig('./plots/sim_dist_%s.png' % (suffix))
    plt.clf()

if __name__ == "__main__":
    # read articles
    articles = pd.read_csv('./data/news_articles_small.csv')
    articles.set_index('News_ID', inplace=True)

    articles_original = articles.copy()

    # convert articles to sets of shingles
    t = time.time()
    articles['article'] = articles['article'].apply(to_shingles)
    plot_jaccard_distribution(articles, 'base')
    print('Plotting similarity distribution without pre-processing took', time.time() - t, 'seconds')

    # convert articles to sets of shingles using punctuation filtering
    t = time.time()
    _filter = partial(to_shingles, filter_punctuation=True)
    articles['article'] = articles_original['article'].apply(_filter)
    plot_jaccard_distribution(articles, 'filter_punctuation')
    print('Plotting similarity distribution with punctuation filtering took', time.time() - t, 'seconds')

    # convert articles to sets of shingles using stopword filtering
    t = time.time()
    _filter = partial(to_shingles, filter_stopwords=True)
    articles['article'] = articles_original['article'].apply(_filter)
    plot_jaccard_distribution(articles, 'filter_stopwords')
    print('Plotting similarity distribution with stopword filtering took', time.time() - t, 'seconds')

    # convert articles to sets of shingles using capitalizaition removal
    t = time.time()
    _filter = partial(to_shingles, remove_capitalization=True)
    articles['article'] = articles_original['article'].apply(_filter)
    plot_jaccard_distribution(articles, 'remove_capitalization')
    print('Plotting similarity distribution with capitalization removal took', time.time() - t, 'seconds')

    # convert articles to sets of shingles using only 3-grams that start with a stopword
    t = time.time()
    _filter = partial(to_shingles, stopword_start=True)
    articles['article'] = articles_original['article'].apply(_filter)
    plot_jaccard_distribution(articles, 'stopword_start')
    print('Plotting similarity distribution with only using 3-grams that start with a stopword took', time.time() - t, 'seconds')

    # convert articles to sets of shingles using only 3-grams that start with a stopword and all other possible filters
    t = time.time()
    _filter = partial(to_shingles, stopword_start=True, filter_punctuation=True, remove_capitalization=True)
    articles['article'] = articles_original['article'].apply(_filter)
    plot_jaccard_distribution(articles, 'stopword_start_filters', True)
    print('Plotting similarity distribution with only using 3-grams that start with a stopword and all other possible filters took', time.time() - t, 'seconds')
