import click
import logging
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
project_data_dir = project_dir.joinpath(
    'data')
raw_books_data_path = project_data_dir.joinpath(
    'raw', 'books.csv')
googlebooks_data_path = project_data_dir.joinpath(
    'external', 'googlebooks_volumes.json')
openbooks_data_path = project_data_dir.joinpath(
    'external', 'openbooks_volumes.json')
outfile_path = project_data_dir.joinpath('tidy', 'books.csv')


@click.command()
@click.option('--raw_books_data_path', default=raw_books_data_path,
              help='.csv path to raw_books_data')
@click.option('--googlebooks_data_path', default=googlebooks_data_path,
              help='.json path to googlebooks data')
@click.option('--openbooks_data_path', default=openbooks_data_path,
              help='.json path to open library data')
@click.option('--outfile_path', default=outfile_path,
              help='.csv path for tidy books data')
def main(raw_books_data_path, googlebooks_data_path,
         openbooks_data_path, outfile_path):

    logger = logging.getLogger(__name__)
    logger.info(
        'PROCESS STARTED: Creating tidy books data using raw books data from \
        %s' % (raw_books_data_path))

    # Read books data
    books = pd.read_csv(raw_books_data_path)
    books['NoDashISBN'] = books['ISBN'].apply(
        lambda x: str(x.replace('-', '')))
    logger.info('Read and formatted books data')

    # Read and prep googlebooks json file
    with googlebooks_data_path.open() as json_data:
        googlebooks_volumes = json.load(json_data)
    googlebooks_df = googlebooks_json_to_df(googlebooks_volumes)
    logger.info('Prepped googlebooks data')

    # Read and prep openlibrary books json file
    with openbooks_data_path.open() as json_data:
        openbooks_volumes = json.load(json_data)
    openbooks_df = openbooks_json_to_df(openbooks_volumes)
    logger.info('Prepped openlibrary data')

    df = tidy_books_data(books, googlebooks_df, openbooks_df)
    df.to_csv(outfile_path, index=False, encoding='utf-8')
    logger.info('Saved books data to %s' % (outfile_path))
    logger.info('PROCESS COMPLETED')


def tidy_books_data(raw_books_data, googlebooks_df, openbooks_df):
    # Merge the books data with googlebooks and openbooks data.
    merged = raw_books_data.merge(
        googlebooks_df, how='left', on='NoDashISBN').merge(
        openbooks_df, how='left', on='NoDashISBN',
        suffixes=['_googlebooks', '_openbooks'])

    for col in ['ISBN_10', 'ISBN_13', 'authors', 'pageCount',
                'publishedDate', 'publisher', 'subtitle',
                'thumbnail_link', 'title']:
        merged[col] = merged.apply(
            lambda row: row[col + '_googlebooks']
            if row[col + '_googlebooks'] is not np.nan
            else row[col + '_openbooks'], axis=1)

    merged.rename({
        'Ownership': 'ownership',
        'HeHasRead': 'he_has_read',
        'NoDashISBN': 'no_dash_isbn',
        'publishedDate': 'published_date',
        'pageCount': 'page_count',
        'Category': 'category',
        'SubCategory': 'subcategory'
    }, axis='columns', inplace=True)

    required_cols = ['title', 'subtitle', 'ownership', 'he_has_read',
                     'no_dash_isbn', 'has_googlebooks_data',
                     'has_openbooks_data', 'authors', 'publisher',
                     'published_date', 'page_count',
                     'description', 'categories', 'category', 'subcategory',
                     'subjects', 'subject_places', 'googlebooks_link',
                     'openbooks_link', 'thumbnail_link',
                     'dewey_decimal_class', 'ISBN_10', 'ISBN_13']

    df = merged[required_cols].copy()
    return df


def googlebooks_json_to_df(googlebooks_volumes):
    data = []
    for volume in googlebooks_volumes:
        if 'items' in volume['response'].keys():
            v = volume['response']['items'][0]['volumeInfo']

            d = {
                'has_googlebooks_data': 1,
                'NoDashISBN': volume['no_dash_isbn'],
                'googlebooks_link': volume['response']['items'][0]['selfLink'],
            }

            for k in ['title', 'subtitle', 'publisher', 'publishedDate',
                      'description', 'pageCount']:
                if k in v.keys():
                    d[k] = v[k]

            for k in ['authors', 'categories']:
                if k in v.keys():
                    d[k] = ';'.join([x for x in v[k]])

            if 'imageLinks' in v.keys():
                d['thumbnail_link'] = v['imageLinks']['thumbnail']

            if 'industryIdentifiers' in v.keys():
                for i in v['industryIdentifiers']:
                    if i['type'] == 'ISBN_13':
                        d['ISBN_13'] = str(i['identifier'])
                    if i['type'] == 'ISBN_10':
                        d['ISBN_10'] = str(i['identifier'])

            data.append(d)
    googlebooks_df = pd.DataFrame(data)
    return googlebooks_df


def openbooks_json_to_df(openbooks_volumes):
    data = []
    for volume in openbooks_volumes:
        if volume['response']:
            no_dash_isbn = volume['no_dash_isbn']
            v = volume['response']['ISBN:' + no_dash_isbn]

            d = {
                'has_openbooks_data': 1,
                'NoDashISBN': no_dash_isbn,
                'openbooks_link': v['url'],
            }

            for k in ['title', 'subtitle', 'publish_date',
                      'description', 'number_of_pages']:
                if k in v.keys():
                    d[k] = v[k]

            for k in ['publishers', 'authors', 'subjects', 'subject_places']:
                if k in v.keys():
                    d[k] = ';'.join([x['name'] for x in v[k]])

            if 'cover' in v.keys():
                d['thumbnail_link'] = v['cover']['small']

            if 'identifiers' in v.keys():
                if 'isbn_13' in v['identifiers'].keys():
                    d['ISBN_13'] = ';'.join(
                        [x for x in v['identifiers']['isbn_13']])
                if 'isbn_10' in v['identifiers'].keys():
                    d['ISBN_10'] = ';'.join(
                        [x for x in v['identifiers']['isbn_10']])

            if 'classifications' in v.keys():
                if 'dewey_decimal_class' in v['classifications'].keys():
                    d['dewey_decimal_class'] = ';'.join(
                        [x for x in v['classifications']['dewey_decimal_class']])

            data.append(d)
    openbooks_df = pd.DataFrame(data)
    openbooks_df.rename({
        'publishers': 'publisher',
        'publish_date': 'publishedDate',
        'number_of_pages': 'pageCount'
    }, axis='columns', inplace=True)

    return openbooks_df


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
