import os
import pandas as pd

from unittest import TestCase, mock

from active_companies.src.workflows.validation import ActiveCompanies
from utils.data_connection.source_manager import Connector


class TestActiveCompanies(TestCase):
    @mock.patch.dict(os.environ, {'DB_USER': 'root'})
    @mock.patch.dict(os.environ, {'DB_PASSWORD': ''})
    @mock.patch.dict(os.environ, {'DB_HOST': 'localhost'})
    @mock.patch.dict(os.environ, {'DB_PORT': '3306'})
    def setUp(self):
        db_connector = Connector(os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"),
                                 os.getenv("DB_PORT"))
        self.active_companies = ActiveCompanies(db_connector=db_connector)

    def tearDown(self):
        del self.active_companies

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_php_active_companies_structure(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [['XPTO']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.active_companies.get_php_active_companies()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertTrue('company_id' in result.columns)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_valid_php_active_companies_parse(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [['1,2,3']]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        result = self.active_companies.get_php_active_companies()
        self.assertTrue(pd.DataFrame.equals(result, pd.DataFrame(['1', '2', '3'], columns=["company_id"])))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_no_php_active_companies_exception(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = self.active_companies.get_php_active_companies()
        self.assertTrue(pd.DataFrame.equals(result, pd.DataFrame([], columns=["company_id"])))

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_identify_company_labels_match(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [3, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None],
                                             [4, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None]]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        true_companies = pd.DataFrame([1, 2, 3, 4],
                                      columns=['id'])
        selected_companies = pd.DataFrame([1, 2, 3, 4],
                                          columns=['company_id'])

        labels = self.active_companies.identify_company_labels(analytics_active_companies=true_companies,
                                                               php_active_companies=selected_companies)

        expected_result = pd.DataFrame([[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 1],
                                        [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 1],
                                        [3, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None, 1, 1],
                                        [4, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None, 1, 1]],
                                       columns=['id', 'name', 'domain', 'created_at', 'language', 'is_enabled',
                                                'deleted_at', 'implementation_python', 'implementation_php'])

        assert expected_result.equals(labels)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_identify_company_labels_match_partial(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [5, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None],
                                             [6, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None]]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        true_companies = pd.DataFrame([1, 2],
                                      columns=['id'])
        selected_companies = pd.DataFrame([1, 2, 3],
                                          columns=['company_id'])

        labels = self.active_companies.identify_company_labels(analytics_active_companies=true_companies,
                                                               php_active_companies=selected_companies)

        expected_result = pd.DataFrame([[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 1],
                                        [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 1]],
                                       columns=['id', 'name', 'domain', 'created_at', 'language', 'is_enabled',
                                                'deleted_at', 'implementation_python', 'implementation_php'])

        assert expected_result.equals(labels)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_identify_company_labels_no_match_php(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [5, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None],
                                             [6, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None]]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        true_companies = pd.DataFrame([1, 2],
                                      columns=['id'])
        selected_companies = pd.DataFrame([7, 8],
                                          columns=['company_id'])

        labels = self.active_companies.identify_company_labels(analytics_active_companies=true_companies,
                                                               php_active_companies=selected_companies)

        expected_result = pd.DataFrame([[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 0],
                                        [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20', 1, 0]],
                                       columns=['id', 'name', 'domain', 'created_at', 'language', 'is_enabled',
                                                'deleted_at', 'implementation_python', 'implementation_php'])

        assert expected_result.equals(labels)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_identify_company_labels_no_match_python(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [5, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None],
                                             [6, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None]]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        true_companies = pd.DataFrame([7, 8],
                                      columns=['id'])
        selected_companies = pd.DataFrame([1, 2],
                                          columns=['company_id'])

        labels = self.active_companies.identify_company_labels(analytics_active_companies=true_companies,
                                                               php_active_companies=selected_companies)

        expected_result = pd.DataFrame([[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20', 0, 1],
                                        [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20', 0, 1]],
                                       columns=['id', 'name', 'domain', 'created_at', 'language', 'is_enabled',
                                                'deleted_at', 'implementation_python', 'implementation_php'])

        assert expected_result.equals(labels)

    @mock.patch('utils.data_connection.source_manager.pymysql', autospec=True)
    def test_verify_accuracy(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [[1, 'xpto1', 'xpto.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [2, 'xpto2', 'xpto2.com', '2019-10-20', 'de_de', 1, '2019-10-20'],
                                             [3, 'xpto3', 'xpto3.com', '2019-10-20', 'de_de', 1, None],
                                             [4, 'xpto4', 'xpto4.com', '2019-10-20', 'de_de', 1, None]]
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        true_companies = pd.DataFrame([1, 2, 3, 4],
                                      columns=['id'])
        selected_companies = pd.DataFrame([1, 2, 3, 4],
                                          columns=['company_id'])

        labels = self.active_companies.identify_company_labels(analytics_active_companies=true_companies,
                                                               php_active_companies=selected_companies)

        accuracy = self.active_companies.verify_accuracy(labels=labels)

        assert accuracy == 100.0
