import pandas as pd
from preprocessing import to_shingles

# Read articles
articles = pd.read_csv('./data/news_articles_small.csv')

# Create shingles
articles['article'] = articles['article'].apply(to_shingles)
print(articles.head())