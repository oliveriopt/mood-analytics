import json
import logging
import multiprocessing

import numpy as np
import time

import sentiment_analysis.src.constants as cons

from nested_lookup import nested_lookup
from collections import defaultdict
from utils.data_connection.api_data_manager import APISourcesFetcher
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from google.cloud.language_v1 import LanguageServiceClient
from utils.utilities import list_2_chunks, MAX_COMPANY_EXECUTION_LIMIT
from utils.data_connection.redis_manager import RedisManager
from sentiment_analysis.src.managers.EntityManager import EntityManager

logger = logging.getLogger()


class TopicsManager(EntityManager):
    """
    Manager for all operations on survey_replies
    """

    def __init__(self, api_manager: APISourcesFetcher, company_ids: list,
                 google_client: LanguageServiceClient, redis_manager: RedisManager, period: dict = None):
        super().__init__(api_manager=api_manager, period=period, google_client=google_client,
                         redis_manager=redis_manager, company_ids=company_ids)

    def fetch_data(self) -> None:
        """
        Fetches data from sources
        """
        self._data = self.api_manager.get_topics(company_ids=self.company_ids)

    @staticmethod
    def __count_filter_topics(raw_topic_entities: list) -> dict:
        """
        Count and filter keys
        :param raw_topic_entities: list of entities text
        :return:
        """
        topic_entities = ClientsLanguageSentiment.count_entities(entities=raw_topic_entities)
        topic_entities = ClientsLanguageSentiment.filter_black_list(entities=topic_entities)

        return topic_entities

    def insert_topics_entities(self, company_id: str, topic_id: str, data: dict):
        """
        Saves information into the company_topic_entities database.
        :param company_id: id of the company
        :param topic_id: id of the topic
        :param data: dict containing data topic information
        :return
        """

        topic_categories = ','.join(list(set(nested_lookup(cons.TOPIC_ENTITIES_TYPE, data)[0])))
        raw_topic_entities = nested_lookup(cons.TOPIC_ENTITIES, data)
        topic_entities = self.__count_filter_topics(raw_topic_entities)

        self.api_manager.insert_topic_entities(company_id=company_id,
                                               topic_id=topic_id,
                                               year=self.period.get("end_year"),
                                               week=self.period.get("end_week"),
                                               entities_categories=topic_categories,
                                               entities_tags=json.dumps(topic_entities, ensure_ascii=False))

    def process_topics_per_company(self, company_id: str):

        company_data = self._data[self._data["company_id"] == company_id]
        data_grouped = company_data.groupby(['company_id', cons.TOPIC_ID, cons.TOPIC_CONTENT])[
            cons.TOPIC_COMMENT].apply(
            '.'.join).reset_index()

        for row in data_grouped.itertuples():
            data = defaultdict(lambda: defaultdict(dict))
            raw_topic_content = row.topic_content

            # Checks if topic_comment after filtering it still has some valid content
            if raw_topic_content is not None:
                logger.info(msg=f"Processing company {company_id}.")

                raw_topic_comment_content = row.topic_comment
                merged_content = raw_topic_content + '. ' + raw_topic_comment_content
                topic_comment_content = self._clean_comments(comment=merged_content)
                entities_text, entities_type = self._process_entities(topic_comment_content)

                # No entities detected
                if len(entities_text) == 0:
                    logger.info(msg=f"No topic entities for company {company_id}.")
                    continue

                if topic_comment_content and len(topic_comment_content) > 0:
                    data.update(topic_content=raw_topic_content,
                                entities_text=entities_text,
                                entities_type=list(set(entities_type)))

                    topic_id = row.topic_id
                    self.insert_topics_entities(company_id=company_id,
                                                topic_id=topic_id,
                                                data=data)

    def save_topics(self, calculate_score=False, multi_processes=False) -> None:
        """
        Processes topics and saves entities information into Mysql
        :param calculate_score: if calculates score using gcloud
        :param multi_processes: Activates multiprocessing
        :return:
        """

        if self._data.empty:
            logger.info(msg=f"No topics to be processed.")
            return

        self._data[cons.TOPIC_CONTENT].replace('', np.nan, inplace=True)
        self._data[cons.TOPIC_CONTENT].replace('--deleted-content--', np.nan, inplace=True)
        self._data = self._data.dropna(subset=[cons.TOPIC_CONTENT]).reset_index(drop=True)

        if not multi_processes:
            for company_id in list(self._data["company_id"].unique()):
                self.process_topics_per_company(company_id=company_id)
                time.sleep(1)
        else:
            target_companies = list(list_2_chunks(slice=self._data["company_id"].unique(),
                                                  limit=MAX_COMPANY_EXECUTION_LIMIT))
            for company_id_set in target_companies:
                processes = []
                for company_id in company_id_set:
                    p = multiprocessing.Process(target=self.process_topics_per_company,
                                                args=(company_id, calculate_score))
                    processes.append(p)
                    p.start()

                for process in processes:
                    process.join()

                # TODO: To avoid hitting the minute quota of GCloud
                time.sleep(30)

    def __parse_topic_content(self, row, calculate_score=False) -> bool:
        """
        Parses and formats topic content
        :param row: Topic row information
        :param calculate_score: Controls if sentiment is calculated for each text field
        :return: Valid topic content
        """
        if row.topic_id in self._result[row.company_id]:
            return True

        raw_topic_content = row.topic_content
        topic_content = self._clean_comments(comment=raw_topic_content)
        entities_text, entities_type = self._process_entities(topic_content)

        if topic_content is not None and len(topic_content) > 0:
            self._result[row.company_id][row.topic_id].update({})
            topic_pointer = self._result[row.company_id][row.topic_id]

            _, sentiment = self._process_sentiment(company_id=row.company_id, text=topic_content)

            topic_pointer.update(created_at=row.created_at)
            topic_pointer.update(headline={
                cons.TOPIC_CONTENT: raw_topic_content,
                cons.TOPIC_ENTITIES: entities_text,
                cons.TOPIC_ENTITIES_TYPE: list(
                    set(entities_type)),
                cons.TOPIC_SENTIMENT: sentiment if calculate_score else ""})
            return True

        return False

    def __parse_topic_comment_content(self, row, calculate_score=False) -> bool:
        """
        Parses and formats topic comment content
        :param row: Topic row information
        :param calculate_score: Controls if sentiment is calculated for each text field
        :return: Valid topic content
        """
        raw_topic_comment_content = row.topic_comment
        topic_comment_content = self._clean_comments(comment=raw_topic_comment_content)

        if topic_comment_content is not None and len(topic_comment_content) > 0:
            entities_text, entities_type = self._process_entities(topic_comment_content)
            topic_pointer = self._result[row.company_id][row.topic_id]

            if not topic_pointer.get("comments"):
                topic_pointer.update(comments=[])

            _, sentiment = self._process_sentiment(company_id=row.company_id, text=topic_comment_content)

            topic_pointer["comments"].append({cons.TOPIC_COMMENT: raw_topic_comment_content,
                                              cons.TOPIC_ENTITIES: entities_text,
                                              cons.TOPIC_ENTITIES_TYPE: list(
                                                  set(entities_type)),
                                              cons.TOPIC_COMMENT_SENTIMENT: sentiment if calculate_score else ""
                                              })
            return True

        return False

    def process_topics(self, calculate_score=True) -> None:
        """
        Processes sentiment analysis and entities on the comment
        :param calculate_score: Controls if scores are calculated for each text field
        :return:    score of the sentiment of the text
                    entities text: these text are not the constants
                    entities type: these types are constants from a list, more info ver documentation from google cloud
        """
        self._data['topic_content'].replace('', np.nan, inplace=True)
        self._data = self._data.dropna(subset=['topic_content']).reset_index(drop=True)

        for row in self._data.itertuples(index=False):
            valid_topic_content = self.__parse_topic_content(row=row, calculate_score=calculate_score)

            if valid_topic_content:
                self.__parse_topic_comment_content(row=row, calculate_score=calculate_score)

            time.sleep(0.5)
