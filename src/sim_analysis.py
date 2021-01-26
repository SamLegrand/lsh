import pandas as pd
from processing import to_shingles
from jaccard import pairwise_jaccard
from usersettings import usersettings
from functools import partial
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # read articles
    articles = pd.read_csv('./data/news_articles_small.csv')

    # convert articles to sets of shingles
    articles['article'] = articles['article'].apply(to_shingles)

    
    buckets = {i/10: 0 for i in range(0, 10)}
    articles = articles.set_index('News_ID').to_dict()['article']

    # compute Jaccard similarity for each article pair
    pairwise_jaccard(articles, buckets)

    # plot similarity range counts
    lists = buckets.items()
    x, y = zip(*lists)
    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, y)
    plt.xticks(x_pos, x)
    plt.yscale("log")
    plt.show()