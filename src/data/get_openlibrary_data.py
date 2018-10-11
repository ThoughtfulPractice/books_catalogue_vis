import click
import pandas as pd
import requests
import json
import time
from pathlib import Path


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
    # Load manually prepared books data
    books = pd.read_csv(raw_books_data_path)
    books['NoDashISBN'] = books['ISBN'].apply(
        lambda x: str(x.replace('-', '')))

    # Use ISBNs to get info on the books from OpenLibrary Books API
    openbooks_endpoint = 'https://openlibrary.org/api/books'
    openbooks_volumes = []
    for no_dash_isbn in books['NoDashISBN']:
        payload = {'bibkeys': 'ISBN:' + no_dash_isbn,
                   'format': 'json',
                   'jscmd': 'data'
                   }
        r = requests.get(openbooks_endpoint, params=payload)
        openbooks_volumes.append(
            {
                'no_dash_isbn': no_dash_isbn,
                'response': r.json()
            })
        time.sleep(0.2)

    # Save as json file
    with outfile_path.open('wb') as outfile:
        json.dump(openbooks_volumes, outfile,
                  ensure_ascii=False, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
