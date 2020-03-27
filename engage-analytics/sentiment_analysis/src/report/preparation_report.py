import os

from utils.gcloud.nlp_client import NLPGoogleClient
from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.data_connection.redis_manager import RedisManager
from utils.data_connection.source_manager import Connector
from sentiment_analysis.src.managers.topics_manager import TopicsManager
from sentiment_analysis.src.managers.survey_replies_manager import SurveyRepliesManager

from utils.utilities import create_list_weeks_years, custom_year_week_format


class PreparationReport:

    def __init__(self, period: dict, weeks_analyze: int, company_id: str, redis_manager: RedisManager):
        self.list_week_year = create_list_weeks_years(week=period.get("end_week"),
                                                      year=period.get("end_year"),
                                                      number_weeks_analyze=weeks_analyze)
        self.company_id = company_id
        self.g_client = NLPGoogleClient.open_client()
        self.__db_connector = Connector(os.getenv("DB_USER"),
                                        os.getenv("DB_PASSWORD"),
                                        os.getenv("DB_HOST"),
                                        os.getenv("DB_PORT"))
        self.api_source_manager = APISourcesFetcher(db_connector=self.__db_connector)

        self.weeks = custom_year_week_format(year_weeks=self.list_week_year)

        self.topics_manager = TopicsManager(api_manager=self.api_source_manager,
                                            google_client=self.g_client,
                                            company_ids=[self.company_id],
                                            redis_manager=redis_manager,
                                            period=period)

        self.surveys_manager = SurveyRepliesManager(api_manager=self.api_source_manager,
                                                    google_client=self.g_client,
                                                    company_ids=[self.company_id],
                                                    redis_manager=redis_manager,
                                                    period=period)

        self.topics = None
        self.replies = None

    def process_data(self) -> None:
        """
        Processes topic data
        :return:
        """

        self.topics_manager.fetch_data()
        self.surveys_manager.fetch_data()
        self.topics_manager.process_topics()
        self.surveys_manager.process_replies()

        self.topics = self.topics_manager.get_results()
        self.replies = self.surveys_manager.get_results()
