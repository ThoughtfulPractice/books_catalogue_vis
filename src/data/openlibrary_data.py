import click
import pandas as pd
import requests
import json
import time
from pathlib import Path
import logging


# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
project_data_dir = project_dir.joinpath('data')

raw_books_data_path = project_data_dir.joinpath(
    'raw', 'books.csv')
outfile_path = project_data_dir.joinpath(
    'external', 'openbooks_volumes.json')


@click.command()
@click.option('--raw_books_data_path', default=raw_books_data_path,
              help='.csv path to raw_books_data')
@click.option('--outfile_path', default=outfile_path,
              help='.json path to save openlibrary api data')
def main(raw_books_data_path, outfile_path):

    logger = logging.getLogger(__name__)
    logger.info(
        'PROCESS STARTED: Calling for data from Open Library Books API\
        using raw books data from\
        %s' % (raw_books_data_path))

    # Load manually prepared books data
    books = pd.read_csv(raw_books_data_path)
    books = add_nodashisbn_column(books)

    # Use ISBNs to get info on the books from OpenLibrary Books API
    isbns = books['NoDashISBN'].tolist()
    openbooks_volumes = openbooks_api(isbns)

    # Save as json file
    with outfile_path.open('wb') as outfile:
        json.dump(openbooks_volumes, outfile,
                  ensure_ascii=False, indent=4, sort_keys=True)
    logger.info('Data saved to %s' % (outfile_path))
    logger.info('PROCESS COMPLETED')


def openbooks_api(isbns):
    """Takes a list of ISBN number strings and returns json
    data from openlibrary api"""
    openbooks_volumes = []
    openbooks_endpoint = 'https://openlibrary.org/api/books'

    no_dash_isbns = [str(x.replace('-', '')) for x in isbns]

    for isbn in no_dash_isbns:
        payload = {'bibkeys': 'ISBN:' + isbn,
                   'format': 'json',
                   'jscmd': 'data'
                   }
        r = requests.get(openbooks_endpoint, params=payload)
        d = {'no_dash_isbn': isbn,
             'response': r.json()}
        openbooks_volumes.append(d)
        time.sleep(0.2)

    return openbooks_volumes


def add_nodashisbn_column(df):
    df['NoDashISBN'] = df['ISBN'].apply(
        lambda x: str(x.replace('-', '')))
    return df


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
