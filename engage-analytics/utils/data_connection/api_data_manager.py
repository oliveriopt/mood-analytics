"""
Script with modules to connect with the database to prepare sources
"""
import logging
import os
import uuid

import pandas as pd
import utils.data_connection.constant_variables_db as cons

from utils.data_connection.source_manager import Connector
from pypika import Query, Tables, Table, JoinType

logger = logging.getLogger()


class APISourcesFetcher:
    """
    Class to get all the proper Sources with connectors
    """

    def __init__(self, db_connector: Connector, database: str = None):
        """
        :param db_connector: Connector to DB server
        :param database: db name
        """
        self.__db_connnector = db_connector
        self.__insights_db = os.getenv("INSIGHTS_DB_NAME")

        if not database:
            self.__database = os.getenv("API_DB_NAME")
        else:
            self.__database = database

    def __select_source(self, query: str) -> pd.DataFrame:
        """
        Executes Select Queries and transforms to data_connection frames
        :param query: query to be executed
        :return: data_connection frame with values
        """
        try:
            self.__db_connnector.open_connection()
            result = list(self.__db_connnector.select_query(query))
            self.__db_connnector.close_connection()
            result = pd.DataFrame(result)

        except Exception as e:
            logger.error(msg=str(e))
            self.__db_connnector.close_connection()
            return None

        return result

    def __insert_source(self, query: str) -> int:
        """
        Executes Insert Queries and transforms to data_connection frames
        :param query: query to be executed
        :return: execution result
        """
        try:
            self.__db_connnector.open_connection()
            result = self.__db_connnector.insert_query(query)
            self.__db_connnector.close_connection()

        except Exception as e:
            logger.error(msg=str(e))
            self.__db_connnector.close_connection()
            return None

        return result

    def get_companies_info(self, companies_columns_names: list = None) -> pd.DataFrame:
        """
        Get all data from the table companies
        :param companies_columns_names: list of columns names we want to select
        :return: data_connection frame with all the data_connection resulted from the query execution
        """
        if companies_columns_names is None or len(companies_columns_names) == 0:
            companies_columns_names = cons.COMPANIES_COLUMN_NAMES

        companies = Table("`%s`.`%s`" % (self.__database, cons.COMPANY_TABLE))

        query = Query.from_(companies) \
            .select(companies.id,
                    companies.name,
                    companies.domain,
                    companies.created_at,
                    companies.language,
                    companies.is_enabled,
                    companies.deleted_at) \
            .where(companies.deleted_at.isnull()) \
            .where(companies.is_enabled == 1)

        result = self.__select_source(query.get_sql(quote_char=None))

        try:
            result.columns = companies_columns_names
        except Exception as e:
            logger.error(msg=str(e))
            return pd.DataFrame()

        return result

    def get_companies_users(self, users_columns_names: list = None) -> pd.DataFrame:
        """
        Get All data_connection from the table company_users
        :param users_columns_names: list of columns names we want to select
        :return: data_connection frame with all the data_connection resulted from the query execution
        """
        if users_columns_names is None or len(users_columns_names) == 0:
            users_columns_names = cons.COMPANY_USERS_COLUMN_NAMES

        users_table = Table("`%s`.`%s`" % (self.__database, cons.COMPANY_USERS_TABLE))

        q = Query.from_(users_table).select(users_table.id,
                                            users_table.company_id,
                                            users_table.user_id,
                                            users_table.is_general_manager,
                                            users_table.is_admin,
                                            users_table.roles,
                                            users_table.created_at,
                                            users_table.deleted_at,
                                            users_table.is_enabled)

        query = str(q).replace("\"", "")
        result = self.__select_source(query)

        try:
            result.columns = users_columns_names
        except Exception as e:
            logger.error(msg=str(e))
            return pd.DataFrame()
        return result

    def get_surveys_mood(self, surveys_mood_columns_names: list = None) -> pd.DataFrame:
        """
        Get All data_connection from the table surveys_mood
        :param surveys_mood_columns_names: list of columns names we want to select
        :return: data_connection frame with all the data_connection resulted from the query execution
        """
        if surveys_mood_columns_names is None or len(surveys_mood_columns_names) == 0:
            surveys_mood_columns_names = cons.SURVEYS_REPLIES_COLUMN_NAMES

        survey_replies = Table("`%s`.`%s`" % (self.__database, cons.SURVEYS_REPLIES_TABLE))

        q = Query.from_(survey_replies).select(survey_replies.id,
                                               survey_replies.survey_question_id,
                                               survey_replies.user_id,
                                               survey_replies.rating,
                                               survey_replies.created_at,
                                               survey_replies.user_timezone,
                                               survey_replies.system_timezone,
                                               survey_replies.survey_iteration_token_id,
                                               survey_replies.comment,
                                               survey_replies.comment_deleted_at)

        query = str(q).replace("\"", "")
        result = self.__select_source(query)

        try:
            result.columns = surveys_mood_columns_names
        except Exception as e:
            logger.error(msg=str(e))
            return pd.DataFrame()
        return result

    def get_survey_replies_dimensions_questions(self, period: dict, company_ids: list) -> pd.DataFrame:
        """
        Select the data from database
        :param period: period of data to fetch (year_s, week_s, year_e, week_e)
        :param company_ids: company_ids to fetch data from
        :return: dataframe with the data selected
        """
        survey_replies, survey_questions, survey_iterations, questions, surveys, dimensions, feature_flags = Tables(
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_REPLIES_TABLE),
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_QUESTIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_ITERATIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.QUESTIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.DIMENSIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.COMPANY_FF_TABLE)
        )

        week_s = period.get("start_week")
        year_s = period.get("start_year")
        week_e = period.get("end_week")
        year_e = period.get("end_year")

        q = Query.from_(survey_replies) \
            .join(survey_questions).on(survey_questions.id == survey_replies.survey_question_id) \
            .join(survey_iterations).on(survey_iterations.id == survey_questions.survey_iteration_id) \
            .join(surveys).on(surveys.id == survey_iterations.survey_id) \
            .join(questions).on(questions.id == survey_questions.question_id) \
            .join(dimensions).on(dimensions.id == questions.dimension_id) \
            .join(feature_flags, how=JoinType.left).on(surveys.company_id == feature_flags.company_id) \
            .select(survey_replies.id.as_('survey_reply_id'),
                    survey_replies.user_id,
                    survey_replies.rating,
                    survey_replies.created_at,
                    survey_replies.comment,
                    survey_iterations.id.as_('survey_iteration_id'),
                    survey_iterations.created_at,
                    survey_iterations.year,
                    survey_iterations.week,
                    surveys.company_id,
                    questions.type_id,
                    questions.description,
                    questions.dimension_id,
                    questions.week,
                    dimensions.description.as_('dimension_description')) \
            .where(survey_replies.comment.notnull()) \
            .where((feature_flags.company_id.isnull()) |
                   (feature_flags.feature_flag_id != "DISABLE_SURVEY"))

        if week_e is None or year_e is None:
            q = q.where((survey_iterations.week == week_s) & (survey_iterations.year == year_s))
        else:
            logger.info(msg="Fetching survey replies on a time period {}".format(period))
            q = q.where((survey_iterations.week[week_s:week_e]) & (survey_iterations.year[year_s:year_e]))
        if len(company_ids) > 0:
            q = q.where(surveys.company_id.isin(company_ids))

        query = str(q).replace("\"", "")
        result = self.__select_source(query)

        try:
            result.columns = cons.SURVEY_REPLIES_DIMENSIONS_QUESTIONS_COLUMN_NAMES
        except Exception as e:
            logger.error(msg=str(e))
            return pd.DataFrame()
        return result

    def get_topics(self, company_ids: list) -> pd.DataFrame:
        """
        Select topics from db
        :param company_ids: list of company_ids
        :return: dataframe with the topics
        """

        topics, topic_comments, feature_flags = Tables("`%s`.`%s`" % (self.__database, cons.TOPICS_TABLE),
                                                       "`%s`.`%s`" % (self.__database, cons.TOPIC_COMMENTS_TABLE),
                                                       "`%s`.`%s`" % (self.__database, cons.COMPANY_FF_TABLE))

        q = Query.from_(topics) \
            .join(topic_comments).on(topic_comments.company_topic_id == topics.id) \
            .join(feature_flags, how=JoinType.left).on(topics.company_id == feature_flags.company_id) \
            .select(topics.id,
                    topics.company_id,
                    topics.is_archived,
                    topics.content,
                    topics.created_at,
                    topic_comments.content) \
            .where(topics.content.notnull()
                   & topics.deleted_at.isnull()
                   & topics.is_archived == 0) \
            .where((feature_flags.company_id.isnull()) |
                   (feature_flags.feature_flag_id != "DISABLE_TOPICS")) \
            .groupby(topics.id,
                     topics.company_id,
                     topics.content,
                     topic_comments.content)

        if len(company_ids) > 0:
            q = q.where(topics.company_id.isin(company_ids))

        query = str(q).replace("\"", "")
        result = self.__select_source(query)

        if result.empty:
            return pd.DataFrame()

        try:
            result.columns = cons.TOPICS_COLUMN_NAMES
        except Exception as e:
            logger.error(msg=str(e))
            return pd.DataFrame()

        return result

    def get_company_week_from_period(self, year: int, week: int, company_id: str) -> int:
        """
        Select company week of teh company
        :param year: year
        :param week: week
        :param company_id: company id
        :return: number of the week of the company in that given period
        """
        survey_iterations, surveys, survey_questions, questions = Tables(
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_ITERATIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.SURVEYS_QUESTIONS_TABLE),
            "`%s`.`%s`" % (self.__database, cons.QUESTIONS_TABLE))

        q = Query.from_(survey_iterations) \
            .join(surveys).on(surveys.id == survey_iterations.survey_id) \
            .join(survey_questions).on(survey_questions.survey_iteration_id == survey_iterations.id) \
            .join(questions).on(questions.id == survey_questions.question_id) \
            .select(questions.week).distinct() \
            .where((survey_iterations.week == week) & (survey_iterations.year == year)) \
            .where(surveys.company_id == company_id) \
            .where(questions.dimension_id != 1)

        query = str(q).replace("\"", "")
        result = self.__select_source(query)
        return result.at[0, 0]

    def insert_topic_entities(self, company_id: str,
                              topic_id: str,
                              year: int,
                              week: int,
                              entities_categories: str,
                              entities_tags: str):
        """
        Insert entities information regarding a topic.
        :param company_id: uuid of a given company
        :param topic_id: uuid of a given topic
        :param year: year entities are about
        :param week: week entities are about
        :param entities_categories: categories of a topic
        :param entities_tags: json str of word cloud
        :return:
        """
        topic_entities = Table("`%s`.`%s`" % (self.__insights_db, cons.TOPIC_ENTITIES_TABLE))
        query = Query.into(topic_entities) \
            .columns(cons.ENTITIES_TABLE_COMPANY_ID,
                     cons.TOPIC_ENTITIES_TABLE_COMPANY_TOPIC_ID,
                     cons.ENTITIES_TABLE_YEAR,
                     cons.ENTITIES_TABLE_WEEK,
                     cons.TOPIC_ENTITIES_TABLE_CATEGORIES,
                     cons.TOPIC_ENTITIES_TABLE_TAGS) \
            .insert(company_id,
                    topic_id,
                    year,
                    week,
                    entities_categories,
                    entities_tags)

        self.__insert_source(query.get_sql(quote_char=None))

    def insert_survey_iteration_entities(self, company_id: str,
                                         survey_iteration_id: str,
                                         year: int,
                                         week: int,
                                         entities_categories: str,
                                         entities_tags: str):
        """
        Insert entities information regarding a survey_iteration.
        :param company_id: uuid of a given company
        :param survey_iteration_id: uuid of a given survey_iteration
        :param year: year entities are about
        :param week: week entities are about
        :param entities_categories: categories of a topic
        :param entities_tags: json str of word cloud
        :return:
        """
        topic_entities = Table("`%s`.`%s`" % (self.__insights_db, cons.SURVEY_ITERATION_ENTITIES_TABLE))
        query = Query.into(topic_entities) \
            .columns(cons.ENTITIES_TABLE_COMPANY_ID,
                     cons.SURVEY_ENTITIES_TABLE_SURVEY_ITERATION_ID,
                     cons.ENTITIES_TABLE_YEAR,
                     cons.ENTITIES_TABLE_WEEK,
                     cons.TOPIC_ENTITIES_TABLE_CATEGORIES,
                     cons.TOPIC_ENTITIES_TABLE_TAGS) \
            .insert(company_id,
                    survey_iteration_id,
                    year,
                    week,
                    entities_categories,
                    entities_tags)

        self.__insert_source(query.get_sql(quote_char=None))
