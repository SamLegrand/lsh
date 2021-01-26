import pandas as pd
from processing import to_shingles
from utils import compute_jaccard, pairwise_jaccard
from multiprocessing import Pool, Manager
from usersettings import usersettings
from functools import partial
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Read articles
    articles = pd.read_csv('./data/news_articles_small.csv')

    # Convert articles to sets of shingles
    articles['article'] = articles['article'].apply(to_shingles)

    # manager = Manager()
    # buckets = manager.dict({i/10: 0 for i in range(0, 10)})
    buckets = {i/10: 0 for i in range(0, 10)}
    articles = articles.set_index('News_ID').to_dict()['article']
    # article_list = [(k, v) for k, v in articles.items()]
    # pairwise_jaccard_partial = partial(pairwise_jaccard, articles=articles, buckets=buckets)
    # with Pool(usersettings["threads"]) as p:
    #     p.map(pairwise_jaccard_partial, article_list)
    for key1, value1 in articles.items():
        for key2, value2 in articles.items():
            if key1 != key2:
                jaccard_sim = compute_jaccard(value1, value2)
                buckets[jaccard_sim // 0.1 * 0.1] += 1
    lists = buckets.items()
    x, y = zip(*lists)
    # y = [math.log(value) if value != 0 else 0 for value in y]
    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, y)
    plt.xticks(x_pos, x)
    plt.yscale("log")
    plt.show()