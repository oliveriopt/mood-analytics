import os, copy
import numpy
import pandas as pd
import utils.data_connection.constant_variables_db as cons

from utils.data_connection.api_data_manager import APISourcesFetcher
from datetime import datetime, timedelta
from unittest import TestCase, mock
from active_companies.src.models.train.active_companies_algorithm import OliverClassifierTimeSeries
from utils.data_connection.source_manager import Connector
from utils.utilities import get_today_year_week


class TestOliverClassifier(TestCase):
    @mock.patch.dict(os.environ, {'DB_USER': 'root'})
    @mock.patch.dict(os.environ, {'DB_PASSWORD': ''})
    @mock.patch.dict(os.environ, {'DB_HOST': 'localhost'})
    @mock.patch.dict(os.environ, {'DB_PORT': '3306'})
    def setUp(self):
        db_connector = Connector(os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"),
                                 os.getenv("DB_PORT"))
        self.classifier = OliverClassifierTimeSeries(api_sources_fetcher=APISourcesFetcher(db_connector))
        self.first_iteration_reply = (datetime.now() - timedelta(weeks=2))
        self.last_iteration_reply = (datetime.now() - timedelta(weeks=1))

        self.mock_companies = {'id': ['1', '2', '3', '4'],
                               'name': ['xpto1', 'xpto2', 'xpto3', 'xpto4'],
                               'domain': ['xpto.com', 'xpto.com', 'xpto.com', 'xpto.com'],
                               'created_at': ['2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10',
                                              '2019-05-10 10:10:10'],
                               'updated_at': ['2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10',
                                              '2019-05-10 10:10:10'],
                               'language': ['de_DE', 'de_DE', 'en_US', 'de_de'],
                               'is_enabled': [1, 1, 1, 1],
                               'deleted_at': [None, None, None, None]
                               }

        self.mock_company_users = {'id': ['1', '2', '3', '4', '5', '6'],
                                   'company_id': ['1', '1', '1', '1', '1', '2'],
                                   'user_id': ['1', '2', '3', '4', '5', '6'],
                                   'is_general_manager': ['1', '1', '0', '1', '0', '0'],
                                   'is_admin': ['0', '0', '1', '0', '0', '1'],
                                   'roles': ['xpto', 'xpto', 'xpto', 'xpto', 'xpto', 'xpto'],
                                   'created_at': ['2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10',
                                                  '2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10'],
                                   'updated_at': ['2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10',
                                                  '2019-05-10 10:10:10', '2019-05-10 10:10:10', '2019-05-10 10:10:10'],
                                   'deleted_at': [None, None, None, None, None, None],
                                   'is_enabled': [1, 1, 1, 1, 1, 1]
                                   }
        self.mock_survey_replies = {'id': ['1', '2', '3', '4', '5', '6', '7', '8'],
                                    'survey_question_id': ['1', '2', '3', '4', '1', '2', '3', '4'],
                                    'user_id': ['1', '2', '3', '4', '1', '2', '3', '4'],
                                    'rating': ['1', '2', '3', '4', '1', '2', '3', '4'],
                                    'created_at': [self.first_iteration_reply, self.first_iteration_reply,
                                                   self.first_iteration_reply,
                                                   self.first_iteration_reply, self.last_iteration_reply,
                                                   self.last_iteration_reply,
                                                   self.last_iteration_reply, self.last_iteration_reply],
                                    'user_timezone': ['Europe/Lisbon', 'Europe/London', 'Europe/London',
                                                      'Europe/Lisbon', 'Europe/Lisbon', 'Europe/London',
                                                      'Europe/London',
                                                      'Europe/Lisbon'],
                                    'system_timezone': ['Europe/Lisbon', 'Europe/London', 'Europe/London',
                                                        'Europe/Lisbon', 'Europe/Lisbon', 'Europe/London',
                                                        'Europe/London',
                                                        'Europe/Lisbon'],
                                    'survey_iteration_token_id': ['token1', 'token2', 'token3', 'token4', 'token1',
                                                                  'token2', 'token3', 'token4'],
                                    'comment': ['xpto', 'xpto', '', 'xpto', 'xpto', 'xpto', '', 'xpto'],
                                    'comment_deleted_at': [None, None, None, None, None, None, None,
                                                           None]
                                    }

    def tearDown(self):
        del self.classifier, self.mock_companies, self.mock_company_users, self.mock_survey_replies

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_surveys_mood', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_identify_active_companies(self, mock_get_companies_info,
                                       mock_get_companies_users,
                                       mock_get_surveys_mood):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)
        mock_get_surveys_mood.return_value = pd.DataFrame(self.mock_survey_replies,
                                                          columns=cons.SURVEYS_REPLIES_COLUMN_NAMES)

        companies_names, year, week = self.classifier.identify_active_companies()
        year, week = get_today_year_week()

        self.assertFalse(companies_names.empty)
        self.assertIsInstance(year, int)
        self.assertIsInstance(week, int)
        self.assertTrue(companies_names['id'][0] == '1')

        self.assertEqual(year, year)
        self.assertEqual(week, week)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_no_valid_companies(self, mock_get_companies_info):
        mock_get_companies_info.return_value = pd.DataFrame()

        result, _, _ = self.classifier.identify_active_companies()
        self.assertTrue(result.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_disabled_companies(self, mock_get_companies_info):
        mock_companies = copy.deepcopy(self.mock_companies)
        mock_companies['is_enabled'][0] = 0

        mock_get_companies_info.return_value = pd.DataFrame(mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.assertFalse(pd.DataFrame.equals(self.classifier.companies, self.classifier.viable_companies))
        self.assertTrue(self.classifier.viable_companies.id.count() == 3)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_deleted_companies(self, mock_get_companies_info):
        mock_companies = copy.deepcopy(self.mock_companies)
        mock_companies['deleted_at'][0] = '2019-05-10 10:10:10'

        mock_get_companies_info.return_value = pd.DataFrame(mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.assertFalse(pd.DataFrame.equals(self.classifier.companies, self.classifier.viable_companies))
        self.assertTrue(self.classifier.viable_companies.id.count() == 3)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_blacklisted_companies(self, mock_get_companies_info):
        mock_companies = copy.deepcopy(self.mock_companies)
        mock_companies['domain'][0] = 'guerrilla.net'

        mock_get_companies_info.return_value = pd.DataFrame(mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.assertFalse(pd.DataFrame.equals(self.classifier.companies, self.classifier.viable_companies))
        self.assertTrue(self.classifier.viable_companies.id.count() == 3)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_disabled_users(self, mock_get_companies_info, mock_get_companies_users):
        mock_company_users = copy.deepcopy(self.mock_company_users)
        mock_company_users['is_enabled'][5] = 0

        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(viable_companies=self.classifier.viable_companies)

        self.assertFalse(pd.DataFrame.equals(self.classifier.users, self.classifier.viable_users))
        self.assertTrue(self.classifier.viable_users.id.count() == 5)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_deleted_users(self, mock_get_companies_info, mock_get_companies_users):
        mock_company_users = copy.deepcopy(self.mock_company_users)
        mock_company_users['deleted_at'][5] = '2019-05-10 10:10:10'

        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(viable_companies=self.classifier.viable_companies)

        self.assertFalse(pd.DataFrame.equals(self.classifier.users, self.classifier.viable_users))
        self.assertTrue(self.classifier.viable_users.id.count() == 5)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_more_than_5_users(self, mock_get_companies_info, mock_get_companies_users):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(viable_companies=self.classifier.viable_companies)

        self.assertFalse(pd.DataFrame.equals(self.classifier.users, self.classifier.viable_users))
        self.assertTrue(self.classifier.viable_users.id.count() == 5)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_surveys_mood', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_surveys_creation_date(self, mock_get_companies_info,
                                          mock_get_companies_users,
                                          mock_get_surveys_mood):
        mock_survey_replies = copy.deepcopy(self.mock_survey_replies)
        mock_survey_replies['created_at'][7] = datetime.now()

        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)
        mock_get_surveys_mood.return_value = pd.DataFrame(mock_survey_replies,
                                                          columns=cons.SURVEYS_REPLIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(viable_companies=self.classifier.viable_companies)

        self.classifier.set_surveys_mood()
        year, week = get_today_year_week()
        self.classifier._surveys_steps(viable_users=self.classifier.viable_users, year=year, week=week)

        self.assertFalse(pd.DataFrame.equals(self.classifier.surveys_mood, self.classifier.viable_surveys))
        self.assertTrue(self.classifier.viable_surveys.id.count() == 7)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_filter_recently_created_companies(self, mock_get_companies_info):
        mock_companies = copy.deepcopy(self.mock_companies)
        mock_companies['created_at'][0] = datetime.now()

        mock_get_companies_info.return_value = pd.DataFrame(mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.assertFalse(pd.DataFrame.equals(self.classifier.companies, self.classifier.viable_companies))
        self.assertTrue(self.classifier.viable_companies.id.count() == 3)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_no_valid_users(self, mock_get_companies_info, mock_get_companies_users):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame()

        result, _, _ = self.classifier.identify_active_companies()
        self.assertTrue(result.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_surveys_mood', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_no_valid_surveys(self, mock_get_companies_info, mock_get_companies_users, mock_get_surveys_mood):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)
        mock_get_surveys_mood.return_value = pd.DataFrame()

        result, _, _ = self.classifier.identify_active_companies()
        self.assertTrue(result.empty)

    def test_delay_weeks(self):
        self.classifier.delay_weeks = 11
        self.assertEqual(self.classifier.delay_weeks, 10)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_companies_correct_transformation(self, mock_get_companies_info):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.assertIsNot(self.classifier.companies, None)
        self.assertIsInstance(self.classifier.companies, pd.DataFrame)
        self.assertFalse(self.classifier.companies.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_companies_empty_return(self, mock_get_companies_info):
        mock_get_companies_info.return_value = pd.DataFrame()
        self.classifier.set_companies()

        with self.assertRaises(Exception):
            self.classifier._prepare_viable_companies()

            self.assertIsNot(self.classifier.companies, None)
            self.assertRaises(Exception, self.classifier._prepare_viable_companies)
            self.assertIsInstance(self.classifier.companies, pd.DataFrame)
            self.assertTrue(self.classifier.companies.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_users_correct_transformation(self, mock_get_companies_info, mock_get_companies_users):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(self.classifier.companies)

        self.assertIsNot(self.classifier.users, None)
        self.assertIsInstance(self.classifier.users, pd.DataFrame)
        self.assertFalse(self.classifier.users.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_users_empty_return(self, mock_get_companies_info, mock_get_companies_users):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame()
        self.classifier.set_users()

        with self.assertRaises(Exception):
            self.classifier._prepare_viable_users(self.classifier.viable_companies)

            self.assertIsNot(self.classifier.users, None)
            self.assertRaises(Exception, self.classifier._prepare_viable_users())
            self.assertIsInstance(self.classifier.users, pd.DataFrame)
            self.assertTrue(self.classifier.users.empty)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_surveys_mood', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_surveys_correct_transformation(self, mock_get_companies_info,
                                                   mock_get_companies_users,
                                                   mock_get_surveys_mood):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)
        mock_get_surveys_mood.return_value = pd.DataFrame(self.mock_survey_replies,
                                                          columns=cons.SURVEYS_REPLIES_COLUMN_NAMES)

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()

        self.classifier.set_users()
        self.classifier._prepare_viable_users(self.classifier.companies)

        self.classifier.set_surveys_mood()
        year, week = get_today_year_week()
        viable_company_ids, last_iteration_year, last_iteration_week = self.classifier._surveys_steps(
            viable_users=self.classifier.viable_users,
            year=year,
            week=week)

        self.assertIsNot(viable_company_ids, None)
        self.assertIsNot(last_iteration_year, None)
        self.assertIsNot(last_iteration_week, None)
        self.assertIsInstance(viable_company_ids, numpy.ndarray)
        self.assertFalse(viable_company_ids.size == 0)

    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_surveys_mood', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_users', autospec=True)
    @mock.patch('utils.data_connection.api_data_manager.APISourcesFetcher.get_companies_info', autospec=True)
    def test_viable_surveys_empty_return(self, mock_get_companies_info,
                                         mock_get_companies_users,
                                         mock_get_surveys_mood):
        mock_get_companies_info.return_value = pd.DataFrame(self.mock_companies,
                                                            columns=cons.COMPANIES_COLUMN_NAMES)
        mock_get_companies_users.return_value = pd.DataFrame(self.mock_company_users,
                                                             columns=cons.COMPANY_USERS_COLUMN_NAMES)
        mock_get_surveys_mood.return_value = pd.DataFrame()

        self.classifier.set_companies()
        self.classifier._prepare_viable_companies()
        self.classifier.set_users()
        self.classifier._prepare_viable_users(viable_companies=self.classifier.companies)

        with self.assertRaises(Exception):
            self.classifier.set_surveys_mood()

            self.assertRaises(Exception, self.classifier._surveys_steps())
            self.assertIsInstance(self.classifier.surveys_mood, pd.DataFrame)
            self.assertTrue(self.classifier.surveys_mood.empty)
