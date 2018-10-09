import pandas as pd
import requests
import json
import time

import os
from dotenv import load_dotenv, find_dotenv
# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()
# load environment variables
load_dotenv(dotenv_path)
googlebooks_api_key = os.environ.get("GOOGLEBOOKS_API_KEY")

# Load manually prepared books data
books = pd.read_csv('../../data/raw/books.csv')
books['NoDashISBN'] = books['ISBN'].apply(lambda x: str(x.replace('-', '')))

# Use ISBNs to get info on the books from GoogleBooks API
googlebooks_endpoint = "https://www.googleapis.com/books/v1/volumes"

googlebooks_volumes = []
for no_dash_isbn in books['NoDashISBN'][0:2]:
    payload = {'q': "isbn:" + no_dash_isbn,
               'key': googlebooks_api_key}
    r = requests.get(googlebooks_endpoint, params=payload)
    googlebooks_volumes.append(
        {'no_dash_isbn': no_dash_isbn,
         'response': r.json()}
    )
    time.sleep(0.2)

# Save as json file
with open('../../data/external/googlebooks_volumes_test.json', 'w') as outfile:
    json.dump(googlebooks_volumes, outfile)
