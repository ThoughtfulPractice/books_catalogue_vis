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


@pytest.fixture(scope='session')
def openbooks_api_response():
    isbns = ["9780823014880", "fo49o28ytb26"]
    response = openlibrary_data.openbooks_api(isbns)
    return response


@pytest.fixture(scope='session')
def googlebooks_api_response():
    isbns = ["9780823014880", "fo49o28ytb26"]
    response = googlebooks_data.googlebooks_api(isbns, GOOGLEBOOKS_API_KEY)
    return response


class TestOpenbooksAPI(object):
    @pytest.mark.api
    def test_returns_list(self, openbooks_api_response):
        assert isinstance(openbooks_api_response, list)

    @pytest.mark.api
    def test_returns_correct_number_of_responses(self, openbooks_api_response):
        assert len(openbooks_api_response) == 2

    @pytest.mark.api
    def assert_returns_isbns_without_dashes(self, openbooks_api_response):
        assert openbooks_api_response[0]['no_dash_isbn'] == '9780823014880'

    def test_adds_nodash_isbn_column_to_df(self):
        df = pd.DataFrame(
            {'ISBN': ["987-654-321-0", "123123123-X"]})

        out = openlibrary_data.add_nodashisbn_column(df)
        assert 'NoDashISBN' in out.columns
        assert out['NoDashISBN'].tolist() == ["9876543210", "123123123X"]


class TestGooglebooksAPI(object):
    @pytest.mark.api
    def test_returns_list(self, googlebooks_api_response):
        assert isinstance(googlebooks_api_response, list)

    @pytest.mark.api
    def test_returns_correct_number_of_responses(self, googlebooks_api_response):
        assert len(googlebooks_api_response) == 2

    @pytest.mark.api
    def test_returns_isbns_without_dashes(self, googlebooks_api_response):
        assert googlebooks_api_response[0]['no_dash_isbn'] == '9780823014880'

    def test_adds_nodash_isbn_column_to_df(self):
        df = pd.DataFrame(
            {'ISBN': ["987-654-321-0", "123123123-X"]})

        out = googlebooks_data.add_nodashisbn_column(df)
        assert 'NoDashISBN' in out.columns
        assert out['NoDashISBN'].tolist() == ["9876543210", "123123123X"]


# Tests for putting required googlebooks data in dataframe
class TestClass2(object):
    def test_hello(self):
        assert True

# Tests for putting required openbooks data in dataframe


# Tests for creating tidy books data
