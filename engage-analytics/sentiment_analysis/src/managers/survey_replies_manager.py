import json
import logging
import multiprocessing
from collections import defaultdict

import numpy as np
import time

from nested_lookup import nested_lookup

import sentiment_analysis.src.constants as cons

from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.utilities import read_json_file, build_translation_question, list_2_chunks, MAX_COMPANY_EXECUTION_LIMIT
from google.cloud.language_v1 import LanguageServiceClient
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from utils.data_connection.redis_manager import RedisManager
from sentiment_analysis.src.managers.EntityManager import EntityManager

logger = logging.getLogger()


class SurveyRepliesManager(EntityManager):
    """
    Manager for all operations on survey_replies
    """

    def __init__(self, api_manager: APISourcesFetcher, period: dict,
                 google_client: LanguageServiceClient, redis_manager: RedisManager, company_ids: list):
        super().__init__(api_manager=api_manager, period=period, google_client=google_client,
                         redis_manager=redis_manager, company_ids=company_ids)
        self.__questions_json_file_en = read_json_file(cons.name_json_file_english)
        self.__questions_json_file_de = read_json_file(cons.name_json_file_german)

    def fetch_data(self) -> None:
        """
        Fetches data from sources
        """
        self._data = self.api_manager.get_survey_replies_dimensions_questions(period=self.period,
                                                                              company_ids=self.company_ids)

    def __attach_question_to_comment(self, comment: str, row: list, language: str) -> str:
        """
        take the question and prepare the text to analyze
        :param comment: text already cleaned to analyze
        :param row: features of the survey reply
        :param language: dominant language
        :return: text with the question and the comment already cleaned
        """
        key_question = build_translation_question(dimension=row.dimension_description, week=row.question_week)
        if language == cons.lang_english:
            question = self.__questions_json_file_en[key_question]
        else:
            question = self.__questions_json_file_de[key_question]

        return question + " " + comment

    def insert_survey_reply_entities(self, company_id: str, survey_iteration_id: str, data: dict):
        """
        Saves information into the survey_iteration_entities database.
        :param company_id: id of the company
        :param survey_iteration_id: id of survey iteration
        :param data: dict containing data topic information
        :return
        """

        topic_categories = ','.join(list(set(nested_lookup(cons.TOPIC_ENTITIES_TYPE, data)[0])))
        raw_topic_entities = nested_lookup(cons.TOPIC_ENTITIES, data)
        topic_entities = ClientsLanguageSentiment.count_entities(entities=raw_topic_entities)
        self.api_manager.insert_survey_iteration_entities(company_id=company_id,
                                                          survey_iteration_id=survey_iteration_id,
                                                          year=self.period.get("end_year"),
                                                          week=self.period.get("end_week"),
                                                          entities_categories=topic_categories,
                                                          entities_tags=json.dumps(topic_entities,
                                                                                   ensure_ascii=False))

    def process_replies_per_company(self, company_id):
        company_data = self._data[self._data["company_id"] == company_id]
        data_grouped = company_data.groupby(['company_id', cons.SURVEY_ITERATION_ID])[
            cons.SURVEY_REPLY].apply(
            '. '.join).reset_index()

        for row in data_grouped.itertuples():
            survey_replies = row.comment

            if survey_replies is not None:
                data = defaultdict(lambda: defaultdict(dict))

                logger.info(msg=f"Processing company {company_id}.")

                survey_replies_clean = self._clean_comments(comment=survey_replies)
                entities_text, entities_type = self._process_entities(survey_replies_clean)

                # No entities detected
                if len(entities_text) == 0:
                    logger.info(msg=f"No survey entities for company {company_id}.")
                    continue

                survey_iteration_id = row.survey_iteration_id
                data.update(survey_ccomment=survey_replies_clean,
                            entities_text=entities_text,
                            entities_type=list(set(entities_type)))

                self.insert_survey_reply_entities(company_id=company_id,
                                                  survey_iteration_id=survey_iteration_id,
                                                  data=data)

    def save_entities(self, calculate_score=True, multi_processes=False) -> None:
        """
        Processes survey replies and saves entities information into Mysql
        :param calculate_score: Controls if sentiment is calculated for each text field
        :param multi_processes: Activates multiprocessing
        :return:
        """

        if self._data.empty:
            logger.info(msg=f"No survey replies to be processed.")
            return

        self._data[cons.SURVEY_REPLY].replace('', np.nan, inplace=True)
        self._data[cons.SURVEY_REPLY].replace('--deleted-content--', np.nan, inplace=True)
        self._data = self._data.dropna(subset=[cons.SURVEY_REPLY]).reset_index(drop=True)

        if not multi_processes:
            for company_id in list(self._data["company_id"].unique()):
                self.process_replies_per_company(company_id=company_id)
                time.sleep(1)
        else:
            target_companies = list(list_2_chunks(slice=self._data["company_id"].unique(),
                                                  limit=MAX_COMPANY_EXECUTION_LIMIT))

            for company_id_set in target_companies:
                processes = []
                for company_id in company_id_set:
                    p = multiprocessing.Process(target=self.process_replies_per_company,
                                                args=(company_id, calculate_score))
                    processes.append(p)
                    p.start()

                for process in processes:
                    process.join()

                # TODO: To avoid hitting the minute quota of GCloud
                time.sleep(30)

    def process_replies(self, process_scores_only=False) -> None:
        """
        Processes sentiment analysis and entities on the comment
        :return:
        """
        if self._data.empty:
            logger.warning(msg="No survey replies found.")
            return

        self._data[cons.SURVEY_REPLY].replace('', np.nan, inplace=True)
        self._data[cons.SURVEY_REPLY].replace('--deleted-content--', np.nan, inplace=True)
        survey_replies_with_content = self._data.dropna(subset=[cons.SURVEY_REPLY]).reset_index(
            drop=True)

        for row in survey_replies_with_content.itertuples(index=False):
            comment = self._clean_comments(comment=row.comment)
            period = "%s_%s" % (row.iteration_week, row.iteration_year)

            if self._process_prefix and comment is not None:

                if row.company_id not in self._result:
                    self._result[row.company_id] = {}
                if period not in self._result[row.company_id]:
                    self._result[row.company_id][period] = {}

                text = self.__attach_question_to_comment(comment, row, cons.lang_english)
                score, sentiment = self._process_sentiment(company_id=row.company_id, text=text)

                reply_data = {}

                if process_scores_only:
                    reply_data.update(score=score)
                else:
                    entities_text, entities_type = self._process_entities(comment)

                    reply_data.update(dimension=row.dimension_description)
                    reply_data.update(text=row.comment)
                    reply_data.update(sentiment=sentiment)
                    reply_data.update(entities_text=entities_text,
                                      entities_type=list(set(entities_type)))

                self._result[row.company_id][period][row.survey_reply_id] = {}
                self._result[row.company_id][period][row.survey_reply_id] = reply_data

            time.sleep(0.5)

