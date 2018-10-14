import pandas as pd
from ...src.data import openlibrary_data, googlebooks_data, tidy_books_data
import pytest
import os
import json
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
    def test_returns_correct_number_of_responses(self,
                                                 googlebooks_api_response):
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


class TestGoogleBooksJSONToDataFrame(object):
    def test_contains_required_columns(self, datadir):
        data_path = datadir['googlebooks_volumes_test.json']

        with data_path.open() as json_data:
            googlebooks_volumes = json.load(json_data)
        df = tidy_books_data.googlebooks_json_to_df(googlebooks_volumes)

        required_columns = [
            'title', 'subtitle', 'publisher', 'publishedDate', 'description',
            'pageCount', 'authors', 'categories', 'thumbnail_link',
            'ISBN_10', 'ISBN_13']
        for col in required_columns:
            assert col in df.columns

    def test_contains_all_volumes_with_info(self, datadir):
        data_path = datadir['googlebooks_volumes_test.json']

        with data_path.open() as json_data:
            googlebooks_volumes = json.load(json_data)
        df = tidy_books_data.googlebooks_json_to_df(googlebooks_volumes)

        volumes_with_info =\
            [volume for volume in googlebooks_volumes
                if 'items' in volume['response'].keys()]
        assert len(df) == len(volumes_with_info)


class TestOpenBooksJSONToDataFrame(object):
    def test_contains_required_columns(self, datadir):
        data_path = datadir['openbooks_volumes_test.json']

        with data_path.open() as json_data:
            openbooks_volumes = json.load(json_data)
        df = tidy_books_data.openbooks_json_to_df(openbooks_volumes)

        required_columns = [
            'title', 'subtitle', 'publisher', 'publishedDate',
            'pageCount', 'authors', 'subjects', 'subject_places',
            'thumbnail_link', 'dewey_decimal_class', 'ISBN_10', 'ISBN_13']
        for col in required_columns:
            assert col in df.columns

    def test_contains_all_volumes_with_info(self, datadir):
        data_path = datadir['openbooks_volumes_test.json']

        with data_path.open() as json_data:
            openbooks_volumes = json.load(json_data)
        df = tidy_books_data.openbooks_json_to_df(openbooks_volumes)

        volumes_with_info = \
            [volume for volume in openbooks_volumes if volume['response']]
        assert len(df) == len(volumes_with_info)


class TestTidyBooksData(object):
    def test_contains_required_columns(self, datadir):
        raw_books_path = datadir['raw_books_test.csv']
        books = pd.read_csv(raw_books_path)
        books['NoDashISBN'] = books['ISBN'].apply(
            lambda x: str(x.replace('-', '')))

        googlebooks_path = datadir['googlebooks_volumes_test.json']
        with googlebooks_path.open() as json_data:
            googlebooks_volumes = json.load(json_data)
        googlebooks_df = tidy_books_data.googlebooks_json_to_df(
            googlebooks_volumes)

        openbooks_path = datadir['openbooks_volumes_test.json']
        with openbooks_path.open() as json_data:
            openbooks_volumes = json.load(json_data)
        openbooks_df = tidy_books_data.openbooks_json_to_df(openbooks_volumes)
        df = tidy_books_data.tidy_books_data(
            books, googlebooks_df, openbooks_df)

        required_columns = [
            'title', 'subtitle', 'ownership', 'he_has_read', 'no_dash_isbn',
            'has_googlebooks_data', 'has_openbooks_data', 'authors',
            'publisher', 'published_date', 'page_count', 'description',
            'categories', 'category', 'subcategory', 'subjects',
            'subject_places', 'googlebooks_link', 'openbooks_link',
            'thumbnail_link', 'dewey_decimal_class', 'ISBN_10', 'ISBN_13']
        for col in required_columns:
            assert col in df.columns
