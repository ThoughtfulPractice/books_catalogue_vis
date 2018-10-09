import pandas as pd
import requests
import json
import time

# Load manually prepared books data
books = pd.read_csv('../../data/raw/books.csv')
books['NoDashISBN'] = books['ISBN'].apply(lambda x: str(x.replace('-', '')))

# Use ISBNs to get info on the books from OpenLibrary Books API
openbooks_endpoint = 'https://openlibrary.org/api/books'
openbooks_volumes = []
for no_dash_isbn in books['NoDashISBN'][0:2]:
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
with open('../../data/external/openbooks_volumes.json', 'w') as outfile:
    json.dump(openbooks_volumes, outfile)
