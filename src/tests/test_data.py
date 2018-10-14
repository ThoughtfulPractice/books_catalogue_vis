import pandas as pd
from ...src.data import openlibrary_data
import unittest
import pytest

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
