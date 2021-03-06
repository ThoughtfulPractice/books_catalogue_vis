import click
import pandas as pd
import requests
import json
import time
from pathlib import Path
import logging
import os
from dotenv import load_dotenv, find_dotenv
# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()
# load environment variables
load_dotenv(dotenv_path)

GOOGLEBOOKS_API_KEY = os.getenv("GOOGLEBOOKS_API_KEY")

# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
project_data_dir = project_dir.joinpath('data')

raw_books_data_path = project_data_dir.joinpath(
    'raw', 'books.csv')
outfile_path = project_data_dir.joinpath(
    'external', 'googlebooks_volumes.json')


@click.command()
@click.option('--raw_books_data_path', default=raw_books_data_path,
              help='.csv path to raw_books_data')
@click.option('--outfile_path', default=outfile_path,
              help='.json path to save googlebooks api data')
@click.option('--googlebooks_api_key', default=GOOGLEBOOKS_API_KEY,
              help='your googlebooks api key')
def main(raw_books_data_path, outfile_path, googlebooks_api_key):

    logger = logging.getLogger(__name__)
    logger.info(
      'PROCESS STARTED: Calling for data from Googlebooks API using raw books data \
      from %s' % (raw_books_data_path))

    # Load manually prepared books data
    books = pd.read_csv(raw_books_data_path)
    books = add_nodashisbn_column(books)

    # Use ISBNs to get info on the books from GoogleBooks API
    isbns = books['NoDashISBN'].tolist()
    googlebooks_volumes = googlebooks_api(isbns, googlebooks_api_key)

    # Save as json file
    with outfile_path.open('w') as outfile:
        json.dump(googlebooks_volumes, outfile,
                  ensure_ascii=False, indent=4, sort_keys=True)
    logger.info('Data saved to %s' % (outfile_path))
    logger.info('PROCESS COMPLETED')


def googlebooks_api(isbns, googlebooks_api_key):
    """Takes a list of ISBN number strings and returns json
    data from googlebooks api"""
    googlebooks_volumes = []
    googlebooks_endpoint = "https://www.googleapis.com/books/v1/volumes"

    no_dash_isbns = [str(x.replace('-', '')) for x in isbns]

    for isbn in no_dash_isbns:
        payload = {'q': "isbn:" + isbn,
                   'key': googlebooks_api_key}
        r = requests.get(googlebooks_endpoint, params=payload)
        d = {'no_dash_isbn': isbn,
             'response': r.json()}
        googlebooks_volumes.append(d)
        time.sleep(0.2)

    return googlebooks_volumes


def add_nodashisbn_column(df):
    df['NoDashISBN'] = df['ISBN'].apply(
        lambda x: str(x.replace('-', '')))
    return df


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
