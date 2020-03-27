#!/usr/bin/env python3

import logging
import os
import re
import uuid
import json
import base64

from datetime import datetime, timedelta, date
from isoweek import Week
import sentiment_analysis.src.constants as global_cons

logger = logging.getLogger()

CUSTOM_YEAR_WEEK_AGG = "_"
MAX_COMPANY_EXECUTION_LIMIT = 5


def is_dev_env() -> bool:
    """
    Checks if is development environment
    :return:
    """
    if os.getenv("APP_ENV") == "dev":
        return True
    return False


def get_bucket_child_name() -> str:
    """
    Returns the bucket name based on the APP_ENV
    :return:
    """
    app_env = os.getenv("APP_ENV")

    if app_env not in ("prod", "release"):
        return "staging"
    return app_env


def get_project_path() -> str:
    """
    Gets project root path based on utils location
    :return: absolute path to project root
    """
    return os.path.dirname(os.path.dirname(os.path.normpath(os.path.join(__file__, os.pardir))))


def custom_year_week_format(year_weeks: list) -> list:
    """
    Receives a list of tuples with (week, year) range and transforms into a list of custom format: "WEEK_YEAR"
    :param year_weeks: [(week,year),(week,year),(week,year),...]
    :return:
    """
    periods = [str(i[0]) + CUSTOM_YEAR_WEEK_AGG + str(i[1]) for i in year_weeks]
    periods.sort()

    return periods


def get_checkout_path() -> str:
    """
    Gets mood-analytics checkout dir path, based on the utils location
    :return: absolute path to analytics root
    """
    utilities_path = get_project_path()
    return os.path.dirname(utilities_path)


def set_log_level() -> None:
    """
    Overrides the log level in the logging.ini, depending on the APP_ENV value
    :return:
    """
    switcher = {
        "develop": 'WARNING',
        "release": 'WARNING',
        "prod": 'WARNING',
        "dev": 'DEBUG'
    }
    logger.setLevel(switcher.get(os.getenv("APP_ENV"), "DEBUG"))


def __extract_log_parcels(logging_message: str) -> object:
    re1 = '((?:2|1)\\d{3}(?:-|\\/)(?:(?:0[1-9])|(?:1[0-2]))(?:-|\\/)(?:(?:0[1-9])|(?:[1-2][0-9])|(?:3[0-1]))(?:T|\\s)(?:(?:[0-1][0-9])|(?:2[0-3])):(?:[0-5][0-9]):(?:[0-5][0-9]))'  # Time Stamp 1
    re2 = '.*?'  # Non-greedy match on filler
    re3 = '((?:[a-z][a-z]+))'  # Word 1
    re4 = '.*?'  # Non-greedy match on filler
    re5 = '((?:[a-z][a-z0-9_]*))'  # Variable Name 1
    re6 = '(.)'  # Any Single Character 1
    re7 = '((?:[a-z][a-z]+))'  # Word 2

    rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7, re.IGNORECASE | re.DOTALL)
    m = rg.search(logging_message)
    if m:
        timestamp = m.group(1)
        level = m.group(2)
        dispatcher = m.group(3) + m.group(4) + m.group(5)
        if "-" in logging_message:
            message = logging_message.split(dispatcher + " - ")[1]
        else:
            message = logging_message
    else:
        timestamp = "None"
        level = "None"
        dispatcher = "None"
        message = "None"

    return {"timestamp": timestamp, "level": level, "dispatcher": dispatcher, "message": message}


def create_id() -> str:
    """
    Create a unique id using uuid4
    :return: str of the id
    """
    id_unique = uuid.uuid4()
    return str(id_unique)


def get_today_year_week() -> tuple:
    """
    Get today year and week
    :return: tuple containing all results
    """
    today = datetime.now()
    year, week, weekday = today.isocalendar()

    if weekday == 7:
        today += timedelta(days=1)

    year, week, weekday = today.isocalendar()

    return year, week


def get_last_week() -> tuple:
    """
    Gets last week number based on current one
    :return: int for week number
    """
    today = datetime.now()
    year, week, weekday = today.isocalendar()

    if weekday == 7:
        today += timedelta(days=1)

    today -= timedelta(weeks=1)
    year, week, _ = today.isocalendar()

    return year, week


def get_iterations_year_week(year: int, week: int, delay: int) -> tuple:
    """
    Get iterations year and week based on target week
    :param year: reference year
    :param week: reference week
    :param delay: back delay based on specified year-week
    :return: tuple of iterations ranges
    """
    w = Week(year, week)
    first_iteration = w - delay
    last_iteration = w - (delay - 1)
    return first_iteration.year, first_iteration.week, last_iteration.year, last_iteration.week


def generate_slack_message(message_heading: str, status: bool, logging_message: str) -> str:
    """
    Generates log in a Slack friendly format
    :param message_heading:
    :param status:
    :param logging_message:
    :return: pretty log
    """
    parcels = __extract_log_parcels(logging_message=logging_message)
    return "%s \n -*Status:* %s \n -*Env:* `%s` \n -*Timestamp:* %s \n -*Level:* %s " \
           "\n -*Dispatcher:* %s \n -*Message:* %s" % (
               message_heading,
               ":white_check_mark:" if status else ":x:",
               os.getenv("APP_ENV"),
               parcels["timestamp"],
               parcels["level"],
               parcels["dispatcher"],
               parcels["message"])


def create_list_weeks_years(week: int, year: int, number_weeks_analyze: int) -> list:
    """
    Create list of list with the information of the week and the year, taking into account the break of end of the year
    :param week: last week to analyze
    :param year: year of the week
    :param number_weeks_analyze: number of week to analyze
    :return: list of list with the oairs to analyze the sentiment
    """

    if week <= number_weeks_analyze:
        number_weeks_year_before = int(str(Week.last_week_of_year(year - 1))[-2:])

        list_week = list(
            range(number_weeks_year_before - (number_weeks_analyze - week - 1), number_weeks_year_before + 1)) \
                    + list(range(1, week + 1))

        list_year = [year - 1] * len(
            list(range(number_weeks_year_before - (number_weeks_analyze - week - 1), number_weeks_year_before + 1))) \
                    + [year] * len(list(range(1, week + 1)))


    else:
        list_week = list(range(week - number_weeks_analyze + 1, week + 1))
        list_year = [year] * len(list_week)

    list_w_y = list(zip(list_week, list_year))
    list_w_y = [list(elem) for elem in list_w_y]
    return list_w_y


def extract_values_from_json(obj, key) -> list:
    """
    Extracts recursively values from specific keys.
    :param obj: json object
    :param key: key to extract values from
    :return: list of values for given key types
    """
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, dict):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def read_json_file(name_json_file) -> dict:
    """
    Read json file with the questions
    :return: Dictionaries with the questions
    """

    try:
        with open(get_project_path() + "/assets/i18n/" + str(name_json_file)) as f:
            dict_questions = json.load(f)
    except Exception as e:
        logger.error(msg=str(e))
        return None

    return dict_questions


def extract_first_last_weeks(list_week_year) -> tuple:
    """
    Retunr the first and the last week to analyze
    :param list_week_year: list with the pair (week, year)
    :return: initial pair and final pair with the week and year to analyze
    """
    if len(list_week_year) >= 2:
        week_s = list_week_year[0][0]
        year_s = list_week_year[0][1]
        week_e = list_week_year[len(list_week_year) - 1][0]
        year_e = list_week_year[len(list_week_year) - 1][1]

        if year_s > year_e:
            logger.error(
                msg="Error on the list of analysis, year start is greater that year end")

    if len(list_week_year) < 2:
        week_s = list_week_year[0][0]
        year_s = list_week_year[0][1]
        week_e = None
        year_e = None
        logger.info(
            msg="Error on the list of analysis, the length is < 2, then do not have end pairs of [mont, year], ONLY START")

    return week_s, year_s, week_e, year_e


def build_translation_question(dimension: str, week: int) -> str:
    """
    Builds the PhraseApp key to access QUESTION
    :param dimension: dimension description
    :param week: question week
    :return:
    """
    return "QUESTION_" + dimension.upper() + "_W" + str(week)


def current_week():
    """
    Return current week
    :return:
    """
    return date.today().isocalendar()[1]


def extract_question(json_file: dict, dimension: str, week: int) -> str:
    """
    Extract question from json file
    :param json_file: path of json file
    :param dimension: target dimension
    :param week: company week to know which is the question
    :return: question from json file
    """

    # TODO: Change this once MOOD_QUESTION is standardized to a single key
    if dimension == 'mood':
        key_json = 'QUESTION_MOOD_W0'
    else:
        key_json = build_translation_question(dimension=dimension, week=week)
    question = extract_values_from_json(json_file, key=key_json)
    return question[0]


def extract_dimension(json_file: dict, dimension: str) -> str:
    """
    Extract dimension from json file
    :param json_file: path of json file
    :param dimension: target dimension
    :return: dimension of the question
    """
    key_json = "DIMENSION_" + dimension.upper()
    dimension = extract_values_from_json(json_file, key=key_json)
    return dimension[0]


def get_start_and_end_date_from_calendar_week(year: int, calendar_week: int) -> tuple:
    """
    Return start and end date from calendar
    :param year: year of the analysis
    :param calendar_week: calendar week
    :return:
    """
    monday = datetime.strptime(f'{year}-{calendar_week}-1', "%G-%V-%w").date()
    return monday.strftime("%A, %d %B %Y"), (monday + timedelta(days=4.9)).strftime("%A, %d %B %Y")


def define_color(i: str, j: str) -> str:
    """
    Define color of the font in the report_pdf
    :param i: string of sentiment
    :param j: type of sentiment
    :return: string with the colour
    """
    color = None
    if i == "sentiment":
        if j == global_cons.POSITIVE: color = "green"
        if j == global_cons.NEGATIVE: color = "red"
    return color


def convert_path_image_64(path_file) -> str:
    with open(path_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return str(encoded_string)


def list_2_chunks(slice: list, limit: int):
    """
    Yield successive n-sized chunks from l.
    :param slice: list of values
    :param limit: breaking limit
    """
    for i in range(0, len(slice), limit):
        yield slice[i:i + limit]
