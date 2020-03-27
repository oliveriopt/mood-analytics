import os
import unittest.mock as mock
from unittest import TestCase
from uuid import UUID
from datetime import datetime, timedelta
from utils.utilities import create_id, get_iterations_year_week, get_today_year_week, generate_slack_message, \
    get_checkout_path, is_dev_env, create_list_weeks_years, extract_first_last_weeks, build_translation_question, \
    get_start_and_end_date_from_calendar_week, define_color, get_bucket_child_name, \
    custom_year_week_format, list_2_chunks, read_json_file, extract_dimension, extract_question
import sentiment_analysis.src.constants as global_cons

class TestUtilities(TestCase):

    def setUp(self):
        self.dict_test = {"xpto-xpto-xpto-xpto": {'29_2019':
                                                      {'8abcf6e2-f7e0-45db-9691-51eae607fb41':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']},
                                                       'd6a37bf8-3785-44af-a1bd-8dcc19a8c61e':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']},
                                                       'f1cad55b-c6fb-4ffb-920c-461f74159eb1':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']}},
                                                  '30_2019':
                                                      {'45224527-7137-4451-b747-40e25f4ff146':
                                                          {
                                                              'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                              'score': 0.800000011920929,
                                                              'entities_text': ['manager', 'team lead', 'boss'],
                                                              'entities_type': ['PERSON', 'OTHER', 'PERSON']},
                                                          'aa98f181-6078-441f-a117-613daf2b8502':
                                                              {
                                                                  'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                                  'score': 0.800000011920929,
                                                                  'entities_text': ['manager', 'team lead', 'boss'],
                                                                  'entities_type': ['PERSON', 'OTHER', 'PERSON']},
                                                          'b9d51ac3-2d7e-44c1-8c03-9846712de99f':
                                                              {
                                                                  'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                                  'score': 0.800000011920929,
                                                                  'entities_text': ['manager', 'team lead', 'boss'],
                                                                  'entities_type': ['PERSON', 'OTHER', 'PERSON']}},
                                                  '31_2019':
                                                      {'c8cfca75-c92e-4d7d-adb8-8210ce693e78':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []},
                                                       '6f60e2bd-84b7-402c-87ff-6e7508e6f34f':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []},
                                                       '2ed90395-56d2-41e7-a0da-fe5d5514c2e1':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []}
                                                       }
                                                  }
                          }
        self.us_translations = read_json_file("en_US.json")

    def tearDown(self):
        del self.dict_test

    def test_create_id(self):
        uuid = create_id()
        try:
            val = UUID(uuid, version=4)
        except ValueError:
            # If it's a value error, then the string
            val = "Error"
        assert str(val) == uuid

    def test_list_2_chunks(self):
        test_list = [1, 2, 3, 4]
        result = list(list_2_chunks(slice=test_list, limit=1))

        assert result[0] == [1]
        assert result[1] == [2]
        assert result[2] == [3]
        assert result[3] == [4]

    def test_get_iterations_same_year(self):
        year = 2019
        week = 25
        delay = 2
        first_iteration_year, first_iteration_week, last_iteration_year, last_iteration_week = get_iterations_year_week(
            year=year,
            week=week,
            delay=delay)

        assert isinstance(first_iteration_year, int)
        assert isinstance(last_iteration_year, int)
        assert isinstance(first_iteration_week, int)
        assert isinstance(last_iteration_week, int)
        assert first_iteration_year == last_iteration_year == 2019
        assert first_iteration_week == 23
        assert last_iteration_week == 24

    def test_get_iterations_year_transition(self):
        year = 2019
        week = 2
        delay = 2
        first_iteration_year, first_iteration_week, last_iteration_year, last_iteration_week = get_iterations_year_week(
            year=year,
            week=week,
            delay=delay)

        assert isinstance(first_iteration_year, int)
        assert isinstance(last_iteration_year, int)
        assert isinstance(first_iteration_week, int)
        assert isinstance(last_iteration_week, int)
        assert first_iteration_year == 2018
        assert last_iteration_year == 2019
        assert first_iteration_week == 52
        assert last_iteration_week == 1

    def test_get_today_year_week(self):
        today = datetime.now()
        year, week, weekday = today.isocalendar()

        if weekday == 7:
            today += timedelta(days=1)

        year_mock, week_mock, _ = today.isocalendar()
        year, week = get_today_year_week()

        assert isinstance(year, int)
        assert isinstance(week, int)
        assert year_mock == year
        assert week_mock == week

    def test_get_last_week(self):
        today = datetime.now()
        year, week, weekday = today.isocalendar()

        if weekday == 7:
            today += timedelta(days=1)

        last_week = today - timedelta(weeks=1)

        assert last_week < today
        assert today - last_week == timedelta(days=7)

    def test_valid_generate_slack_message(self):
        message = generate_slack_message(message_heading="This is a test", status=True,
                                         logging_message="2006-02-08 22:20:02,165 ERROR "
                                                         "active_companies_2 ERROR - No active companies from insights")
        assert "Status" in message
        assert "Timestamp" in message
        assert "Level" in message
        assert "Dispatcher" in message
        assert "Message" in message

    def test_invalid_generate_slack_message(self):
        message = generate_slack_message(message_heading="This is a test", status=True,
                                         logging_message="")
        assert "Status" in message
        assert "Timestamp" in message
        assert "Level" in message
        assert "Dispatcher" in message
        assert "Message" in message

    def test_get_checkout_path(self):
        base_dir = get_checkout_path()

        assert isinstance(base_dir, str)

        assert base_dir != ""
        assert os.path.exists(base_dir)

    def extract_dimension(self):
        dimension = extract_dimension(json_file=self.us_translations, dimension="mood")

        assert isinstance(dimension, str)
        assert dimension != ""

    def extract_question(self):
        question = extract_question(json_file=self.us_translations, dimension="mood", week=1)

        assert isinstance(question, str)
        assert question != ""

    def extract_question_week_agnostic(self):
        question = extract_question(json_file=self.us_translations, dimension="mood", week=14)

        assert isinstance(question, str)
        assert question != ""

    @mock.patch.dict(os.environ, {'APP_ENV': 'xpt'})
    def test_is_not_dev_env(self):
        env = is_dev_env()
        assert isinstance(env, bool)
        assert env is False

    @mock.patch.dict(os.environ, {'APP_ENV': 'dev'})
    def test_is_dev_env(self):
        env = is_dev_env()
        assert isinstance(env, bool)
        assert env is True

    @mock.patch.dict(os.environ, {'APP_ENV': 'dev'})
    def test_get_staging_bucket_child_name(self):
        child_bucket = get_bucket_child_name()
        assert isinstance(child_bucket, str)
        assert child_bucket == "staging"

    @mock.patch.dict(os.environ, {'APP_ENV': 'prod'})
    def test_get_bucket_child_name(self):
        child_bucket = get_bucket_child_name()
        assert isinstance(child_bucket, str)
        assert child_bucket == "prod"

    def test_custom_year_week_format(self):
        year_week = [(31, 2019), (30, 2019)]
        transformation = custom_year_week_format(year_week)

        self.assertIsInstance(transformation, list)
        assert transformation[0] == "30_2019"
        assert transformation[1] == "31_2019"

    def test_create_list_weeks_years_with_break(self):
        test_week = 4
        test_year = 2019
        number_weeks_analyze = 5
        list_week_year = create_list_weeks_years(test_week, test_year, number_weeks_analyze)

        assert list_week_year == [[52, 2018], [1, 2019], [2, 2019], [3, 2019], [4, 2019]]

    def test_create_list_weeks_years_without_break(self):
        test_week = 30
        test_year = 2019
        number_weeks_analyze = 5
        list_week_year = create_list_weeks_years(test_week, test_year, number_weeks_analyze)

        assert list_week_year == [[26, 2019], [27, 2019], [28, 2019], [29, 2019], [30, 2019]]

    def test_extract_first_last_weeks_with_break(self):

        list_week_year = [[52, 2018], [1, 2019], [2, 2019], [3, 2019], [4, 2019]]
        week_s, year_s, week_e, year_e = extract_first_last_weeks(list_week_year)

        assert week_s == 52
        assert year_s == 2018
        assert week_e == 4
        assert year_e == 2019

    def test_extract_first_last_weeks_without_break(self):

        list_week_year = [[26, 2019], [27, 2019], [28, 2019], [29, 2019], [30, 2019]]
        week_s, year_s, week_e, year_e = extract_first_last_weeks(list_week_year)

        assert week_s == 26
        assert year_s == 2019
        assert week_e == 30
        assert year_e == 2019

    def test_build_translation_question(self):
        week = 0
        dimension = "mood"

        result = build_translation_question(dimension=dimension, week=week)
        expected = "QUESTION_" + dimension.upper() + "_W" + str(week)

        assert result == expected

    def test_get_start_and_end_date_from_calendar_week(self):
        year = 2019
        calendar_week = 36
        string = get_start_and_end_date_from_calendar_week(year, calendar_week)
        self.assertIsInstance(string, tuple)
        self.assertIsInstance(string[0], str)
        self.assertIsInstance(string[1], str)
        self.assertTrue(string[0], "Monday, 02 September 2019")
        self.assertTrue(string[1], "Friday, 06 September 2019")

    def test_define_color_none(self):
        color = define_color("sentiment", global_cons.NEUTRAL)
        print(color)
        self.assertIsNone(color)

    def test_define_color_green(self):
        color = define_color("sentiment", global_cons.POSITIVE)
        self.assertIsInstance(color, str)
        assert color == "green"

    def test_define_color_red(self):
        color = define_color("sentiment", global_cons.NEGATIVE)
        self.assertIsInstance(color, str)
        assert color == "red"
