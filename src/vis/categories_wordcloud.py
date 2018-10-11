import pandas as pd
import numpy as np
from wordcloud import WordCloud
from palettable.colorbrewer.qualitative import Set3_12
import click
from pathlib import Path
import logging

# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
tidy_books_data_path = project_dir.joinpath(
    'data', 'tidy', 'books.csv')
outfile_dir = project_dir.joinpath('reports', 'figures')
outfile_name = 'categories_wordcloud.png'


@click.command()
@click.option('--tidy_books_data_path', default=tidy_books_data_path,
              help='.csv path to tidy books data')
@click.option('--outfile_name', default=outfile_name,
              help='filename for generated vis')
@click.option('--outfile_dir', default=outfile_dir,
              help='folder path for generated vis')
def main(tidy_books_data_path, outfile_name, outfile_dir):
    logger = logging.getLogger(__name__)
    outfile_path = outfile_dir.joinpath(outfile_name)

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
    logger.info('%s saved to %s' % (outfile_path.stem, outfile_path))


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
