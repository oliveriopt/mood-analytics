import argparse
import logging
import os

from sentiment_analysis.src.managers.survey_replies_manager import SurveyRepliesManager
from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.data_connection.source_manager import Connector
from utils.gcloud.nlp_client import NLPGoogleClient
from utils.utilities import get_last_week, create_list_weeks_years, extract_first_last_weeks, custom_year_week_format
from google.cloud.language_v1 import LanguageServiceClient
from utils.data_connection.factory.redis_factory import RedisFactory
from utils.data_connection.redis_manager import RedisManager
from nested_lookup import nested_lookup

logger = logging.getLogger()


def inject_year_week_sentiment_analysis(db_connector: Connector,
                                        google_client: LanguageServiceClient,
                                        redis_manager: RedisManager,
                                        list_week_year: list,
                                        company_id: str) -> dict:
    """
    Inject the week/year to surveys replies manager
    :param db_connector: connector
    :param google_client: google client
    :param redis_manager: redis manager
    :param list_week_year: list of weeks years
    :param company_id: company target
    :return:
    """

    week_s, year_s, week_e, year_e = extract_first_last_weeks(list_week_year)

    period = {"start_year": year_s,
              "start_week": week_s,
              "end_year": year_e,
              "end_week": week_e}

    survey_replies_manager = SurveyRepliesManager(api_manager=APISourcesFetcher(db_connector=db_connector),
                                                  google_client=google_client,
                                                  redis_manager=redis_manager,
                                                  period=period,
                                                  company_ids=[company_id])
    survey_replies_manager.fetch_data()
    survey_replies_manager.process_replies(process_scores_only=True)

    return survey_replies_manager.get_results()


def persist_result_redis(company_id: str, processing_result: dict, redis_manager) -> None:
    """
    Write the dictionary into redis
    :param company_id: str of company id
    :param redis_manager: redis manager
    :param processing_result: dict to persist into redis
    :return:
    """

    redis_score_field = "score"

    # Empty data
    if not processing_result:
        logger.warning(msg="No data to be persisted in Redis.")
        return

    company_redis_data = redis_manager.retrieve(key=company_id,
                                                field=redis_score_field)
    processed_data = nested_lookup(redis_score_field, processing_result[company_id])

    scores = company_redis_data + processed_data

    redis_manager.persist(key=company_id,
                          field=redis_score_field,
                          data=scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract surveys replies from DB and inject to REDIS')
    parser.add_argument('--year', help='year of the survey')
    parser.add_argument('--week', help='week of the survey')
    parser.add_argument("--number_week_to_insert", help="number of week to agglomerate", default=1)
    parser.add_argument('--company_id', help='target company id', required=True)

    args = parser.parse_args()

    target_year = args.year
    target_week = args.week
    number_week_to_insert = args.number_week_to_insert
    company_id = args.company_id

    if target_week is None or target_year is None:
        target_year, target_week = get_last_week()

    connector = Connector(os.getenv("DB_USER"),
                          os.getenv("DB_PASSWORD"),
                          os.getenv("DB_HOST"),
                          os.getenv("DB_PORT"))

    g_client = NLPGoogleClient.open_client()

    list_week_year = create_list_weeks_years(week=int(target_week),
                                             year=int(target_year),
                                             number_weeks_analyze=int(number_week_to_insert))
    weeks = custom_year_week_format(year_weeks=list_week_year)

    redis_manager = RedisFactory.build()

    processing_result = inject_year_week_sentiment_analysis(db_connector=connector,
                                                            google_client=g_client,
                                                            redis_manager=redis_manager,
                                                            list_week_year=list_week_year,
                                                            company_id=company_id)

    persist_result_redis(company_id=company_id,
                         redis_manager=redis_manager,
                         processing_result=processing_result)
