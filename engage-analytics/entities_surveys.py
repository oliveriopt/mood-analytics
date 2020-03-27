import argparse
import logging.config

import os

import newrelic.agent

from utils.gcloud.nlp_client import NLPGoogleClient
from survey_replies_manager import SurveyRepliesManager
from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.data_connection.source_manager import Connector
from utils.utilities import get_last_week, set_log_level, get_project_path
from utils.data_connection.factory.redis_factory import RedisFactory

logging.config.fileConfig("%s/logging.ini" % get_project_path())
set_log_level()
logger = logging.getLogger()


@newrelic.agent.background_task()
def task():
    parser = argparse.ArgumentParser(description='Run sentiment analysis for survey replies')
    parser.add_argument('--year_start', type=int, help='year start of the survey')
    parser.add_argument('--week_start', type=int, help='week start of the survey')
    parser.add_argument('--year_end', type=int, help='year end of the survey')
    parser.add_argument('--week_end', type=int, help='week end of the survey')
    parser.add_argument('--company_id', type=str, help='target company id')
    args = parser.parse_args()
    target_year_start = args.year_start
    target_week_start = args.week_start
    target_year_end = args.year_end
    target_week_end = args.week_end

    if (target_week_start is None or target_year_start is None) or (target_week_end is None or target_year_end is None):
        target_year, target_week = get_last_week()

        period = {"start_year": target_year,
                  "start_week": target_week,
                  "end_year": target_year,
                  "end_week": target_week}
    else:
        period = {"start_year": target_year_start,
                  "start_week": target_week_start,
                  "end_year": target_year_end,
                  "end_week": target_week_end}

    g_client = NLPGoogleClient.open_client()

    db_connector = Connector(os.getenv("DB_USER"),
                             os.getenv("DB_PASSWORD"),
                             os.getenv("DB_HOST"),
                             os.getenv("DB_PORT"))
    api_source_manager = APISourcesFetcher(db_connector=db_connector)

    redis_manager = RedisFactory.build()

    company_ids = []

    if args.company_id:
        company_ids.append(args.company_id)
    else:
        enabled_companies = api_source_manager.get_companies_info()
        company_ids = list(enabled_companies['id'])

    logger.info(msg=f"Processing {len(company_ids)} companies...")
    surveys_manager = SurveyRepliesManager(api_manager=api_source_manager,
                                           google_client=g_client,
                                           redis_manager=redis_manager,
                                           period=period,
                                           company_ids=company_ids
                                           )

    surveys_manager.fetch_data()
    surveys_manager.save_entities(calculate_score=False)


task()
