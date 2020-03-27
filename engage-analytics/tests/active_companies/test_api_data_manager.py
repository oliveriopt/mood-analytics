import os
import pandas as pd
import utils.data_connection.constant_variables_db as cons

from utils.data_connection.api_data_manager import APISourcesFetcher
from unittest import TestCase, mock
from utils.data_connection.source_manager import Connector


class TestOliverClassifier(TestCase):
    @mock.patch.dict(os.environ, {'DB_USER': 'root'})
    @mock.patch.dict(os.environ, {'DB_PASSWORD': ''})
    @mock.patch.dict(os.environ, {'DB_HOST': 'localhost'})
    @mock.patch.dict(os.environ, {'DB_PORT': '3306'})
    def setUp(self):
        db_connector = Connector(os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"),
                                 os.getenv("DB_PORT"))
        self.api_fetcher = APISourcesFetcher(db_connector=db_connector)

    def tearDown(self):
        del self.api_fetcher

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_companies_info_attributes(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [
            ['XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.api_fetcher.get_companies_info(companies_columns_names=cons.COMPANIES_COLUMN_NAMES)
        result_no_parameter = self.api_fetcher.get_companies_info()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue(list(result.columns) == cons.COMPANIES_COLUMN_NAMES)
        self.assertTrue(pd.DataFrame.equals(result, result_no_parameter))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_company_users_info_attributes(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [
            ['XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO',
             'XPTO', 'XPTO']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.api_fetcher.get_companies_users(users_columns_names=cons.COMPANY_USERS_COLUMN_NAMES)
        result_no_parameter = self.api_fetcher.get_companies_users()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue(list(result.columns) == cons.COMPANY_USERS_COLUMN_NAMES)
        self.assertTrue(pd.DataFrame.equals(result, result_no_parameter))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_survey_moods(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [
            ['XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.api_fetcher.get_surveys_mood(surveys_mood_columns_names=cons.SURVEYS_REPLIES_COLUMN_NAMES)
        result_no_parameter = self.api_fetcher.get_surveys_mood()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue(list(result.columns) == cons.SURVEYS_REPLIES_COLUMN_NAMES)
        self.assertTrue(pd.DataFrame.equals(result, result_no_parameter))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_invalid_companies_info(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = self.api_fetcher.get_companies_info(companies_columns_names=cons.COMPANIES_COLUMN_NAMES)
        self.assertTrue(result.empty)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_invalid_company_users_info(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = self.api_fetcher.get_companies_users(users_columns_names=cons.COMPANY_USERS_COLUMN_NAMES)
        self.assertTrue(result.empty)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_invalid_surveys_mood(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = self.api_fetcher.get_surveys_mood(surveys_mood_columns_names=cons.SURVEYS_REPLIES_COLUMN_NAMES)
        self.assertTrue(result.empty)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_get_topics(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [
            ['XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.api_fetcher.get_topics(company_ids=["XPTO"])
        result_no_parameter = self.api_fetcher.get_topics(company_ids=["XPTO"])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue(list(result.columns) == cons.TOPICS_COLUMN_NAMES)
        self.assertTrue(pd.DataFrame.equals(result, result_no_parameter))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_get_survey_replies_dimensions_questions(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [
            ['XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO',
             'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO', 'XPTO',
             'XPTO', 'XPTO', 'XPTO']]

        period = {"start_year": "XPTO",
                  "start_week": "XPTO",
                  "end_year": "XPTO",
                  "end_week": "XPTO"}

        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.api_fetcher.get_survey_replies_dimensions_questions(period=period,
                                                                          company_ids=["XPTO"])
        result_no_parameter = self.api_fetcher.get_survey_replies_dimensions_questions(period=period,
                                                                                       company_ids=["XPTO"])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue(list(result.columns) == cons.SURVEY_REPLIES_DIMENSIONS_QUESTIONS_COLUMN_NAMES)
        self.assertTrue(pd.DataFrame.equals(result, result_no_parameter))
