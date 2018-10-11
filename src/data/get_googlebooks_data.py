import click
import pandas as pd
import requests
import json
import time
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
import logging


# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
project_data_dir = project_dir.joinpath('data')

raw_books_data_path = project_data_dir.joinpath(
    'raw', 'books.csv')
outfile_path = project_data_dir.joinpath(
    'external', 'googlebooks_volumes.json')

# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()
# load environment variables
load_dotenv(dotenv_path)
googlebooks_api_key = os.environ.get("GOOGLEBOOKS_API_KEY")


@click.command()
@click.option('--raw_books_data_path', default=raw_books_data_path,
              help='.csv path to raw_books_data')
@click.option('--outfile_path', default=outfile_path,
              help='.json path to save googlebooks api data')
@click.option('--googlebooks_api_key', default=googlebooks_api_key,
              help='your googlebooks api key')
def main(raw_books_data_path, outfile_path, googlebooks_api_key):
  
    logger = logging.getLogger(__name__)
    logger.info(
      'PROCESS STARTED: Calling for data from Googlebooks API using raw books data \
      from %s' % (raw_books_data_path))

    # Load manually prepared books data
    books = pd.read_csv(raw_books_data_path)
    books['NoDashISBN'] = books['ISBN'].apply(
        lambda x: str(x.replace('-', '')))

    # Use ISBNs to get info on the books from GoogleBooks API
    googlebooks_endpoint = "https://www.googleapis.com/books/v1/volumes"

    googlebooks_volumes = []
    for no_dash_isbn in books['NoDashISBN']:
        payload = {'q': "isbn:" + no_dash_isbn,
                   'key': googlebooks_api_key}
        r = requests.get(googlebooks_endpoint, params=payload)
        googlebooks_volumes.append(
            {'no_dash_isbn': no_dash_isbn,
             'response': r.json()}
        )
        time.sleep(0.2)

    # Save as json file
    with outfile_path.open('wb') as outfile:
        json.dump(googlebooks_volumes, outfile,
                  ensure_ascii=False, indent=4, sort_keys=True)
    logger.info('Data saved to %s' % (outfile_path))
    logger.info('PROCESS COMPLETED')


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
