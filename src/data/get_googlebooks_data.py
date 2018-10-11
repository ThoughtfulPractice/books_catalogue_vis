import pandas as pd
import requests
import json
import time
from pathlib import Path

import os
from dotenv import load_dotenv, find_dotenv


def main():
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


if __name__ == "__main__":
    main()
