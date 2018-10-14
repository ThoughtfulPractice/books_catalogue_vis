import pandas as pd
from ...src.data import openlibrary_data, googlebooks_data
import pytest
import os
from dotenv import load_dotenv, find_dotenv
# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()
# load environment variables
load_dotenv(dotenv_path)

GOOGLEBOOKS_API_KEY = os.getenv("GOOGLEBOOKS_API_KEY")

# Tests for openlibrary_data.py
@pytest.fixture(scope='session')
def openbooks_api_response():
    isbns = ["9780823014880", "fo49o28ytb26"]
    response = openlibrary_data.openbooks_api(isbns)
    return response


def test_returns_list(openbooks_api_response):
    assert isinstance(openbooks_api_response, list)


def test_returns_correct_number_of_responses(openbooks_api_response):
    assert len(openbooks_api_response) == 2


def assert_returns_isbns_without_dashes(openbooks_api_response):
    assert openbooks_api_response[0]['no_dash_isbn'] == '9780823014880'


def test_adds_nodash_isbn_column_to_df(datadir):
    RAW_BOOKS_PATH = datadir["raw_books.csv"]
    df = pd.read_csv(RAW_BOOKS_PATH)

    out = openlibrary_data.add_nodashisbn_column(df)
    assert 'NoDashISBN' in out.columns
    assert out['NoDashISBN'].equals((df['ISBN'].apply(
        lambda x: str(x.replace('-', '')))))


# Tests for googlebooks_data.py
@pytest.fixture(scope='session')
def googlebooks_api_response():
    isbns = ["9780823014880", "fo49o28ytb26"]
    response = googlebooks_data.googlebooks_api(isbns, GOOGLEBOOKS_API_KEY)
    return response


def test_googlebooks_api_returns_list(googlebooks_api_response):
    assert isinstance(googlebooks_api_response, list)


def test_googlebooks_api_returns_correct_number_of_responses(googlebooks_api_response):
    assert len(googlebooks_api_response) == 2


def assert_googlebooks_api_returns_isbns_without_dashes(googlebooks_api_response):
    assert googlebooks_api_response[0]['no_dash_isbn'] == '9780823014880'


def test_googlebooks_api_adds_nodash_isbn_column_to_df(datadir):
    RAW_BOOKS_PATH = datadir["raw_books.csv"]
    df = pd.read_csv(RAW_BOOKS_PATH)

    out = googlebooks_data.add_nodashisbn_column(df)
    assert 'NoDashISBN' in out.columns
    assert out['NoDashISBN'].equals((df['ISBN'].apply(
        lambda x: str(x.replace('-', '')))))
