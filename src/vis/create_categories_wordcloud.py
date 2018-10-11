import click
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from palettable.colorbrewer.qualitative import Set3_12
from pathlib import Path

# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
tidy_books_data_path = project_dir.joinpath(
    'data', 'tidy', 'books.csv')
outfile_path = project_dir.joinpath(
    'reports', 'figures', 'categories_wordcloud.png')


@click.command()
@click.option('--tidy_books_data_path', default=tidy_books_data_path,
              help='.csv path to tidy books data')
@click.option('--outfile_path', default=outfile_path,
              help='path to save generated wordcloud')
def main(tidy_books_data_path, outfile_path):
    books = pd.read_csv(tidy_books_data_path)
    df = books[books['ownership'] == 'His']

    texts = list(df['category'].values)
    texts = [x.split(";") for x in texts if x is not np.nan]

    # Some stuff in the columns that I don't want to appear in the wordcloud.
    stopwords = [np.nan, 'Protected DAISY', 'In library', 'Accessible book',
                 'Internet Archive Wishlist', 'OverDrive',
                 'Open Library Staff Picks',
                 'Long Now Manual for Civilization',
                 'New York Times bestseller']
    texts = [item.strip() for t in texts for item in t]
    texts = [x for x in texts if x not in stopwords]

    # Wordcloud settings
    wc = WordCloud(width=1080, height=720, max_words=50,
                   background_color='white', colormap=Set3_12.mpl_colormap)

    # Generate word cloud
    wc.generate_from_frequencies(pd.Series(texts).value_counts())

    # Save to file
    wc.to_file(outfile_path)


if __name__ == "__main__":
    main()
