"""
All Active Companies Workflow
"""

import logging.config
import os
import pandas as pd

import utils.data_connection.constant_variables_db as cons
from utils.utilities import generate_slack_message, get_project_path

from utils.data_connection.api_data_manager import APISourcesFetcher

from active_companies.src.implementation.services import get_active_companies
from active_companies.src.models.train.active_companies_algorithm import OliverClassifierTimeSeries
from active_companies.src.models.performance.labels import ConfusionMatrixLabel
from active_companies.src.models.performance.metrics import Evaluation
from active_companies.src.workflows.logs.register import log_active_company
from active_companies.src.workflows.configurations import Parameters
from utils.alerts.slack_message import AlertMessage
from utils.data_connection.source_manager import Connector

logger = logging.getLogger()


class ActiveCompanies:
    def __init__(self, db_connector: Connector):
        self.__db_connector = db_connector
        self.__api_data_fetcher = APISourcesFetcher(db_connector=self.__db_connector)
        self.__default_validation_parameters = {
            'alert': True,
            'user_connection': os.getenv("DB_USER"),  # user to connect to the database
            'pwd_connection': os.getenv("DB_PASSWORD"),  # password to connect to the database
            'host_connection': os.getenv("DB_HOST"),  # host/ip to connect to the database
            'database_app': os.getenv("INSIGHTS_DB_NAME"),  # name of the schema or database to connect
            'port_connection': os.getenv("DB_PORT"),  # port number
            'columns_app': cons.ACTIVE_COMPANIES_COLUMNS,  # List with the columns names of the table with active names
            'table_app': cons.ACTIVE_COMPANIES_TABLE,  # name of the table with active names
            'database_sources': os.getenv("API_DB_NAME"),
            'companies_table_sources': cons.COMPANY_TABLE,
            'companies_columns_names_sources': None,
            'users_table_sources': cons.COMPANY_USERS_TABLE,
            'users_columns_names_sources': None,
            'surveys_mood_table_sources': cons.SURVEYS_REPLIES_TABLE,
            'surveys_mood_columns_names_sources': None,
            'label_name_as_truth_labels': 'implementation_python',
            'label_name_to_validate_labels': 'implementation_php',
            'database_validation': os.getenv("INSIGHTS_DB_NAME"),
            "table_validation": cons.JOBS_ACTIVE_COMPANIES_TABLE,
            "table_columns_validation": cons.JOBS_ACTIVE_COMPANIES_COLUMNS_NAMES,
            "table_detail_validation": cons.JOBS_ACTIVE_COMPANIES_DETAILS_TABLE,
            "table_detail_columns_validation": cons.JOBS_ACTIVE_COMPANIES_DETAILS_COLUMNS_NAMES

        }
        # Split Variables
        self.__levels = ['app', 'classifier', 'sources', 'connection', 'labels', 'validation']
        self.__default_validation_parameters_level = Parameters.split(self.__default_validation_parameters,
                                                                      self.__levels)

    def get_php_active_companies(self) -> pd.DataFrame:
        """
        Get active companies from PHP algorithm
        :return: Dataframe with company info
        """
        php_active_companies = get_active_companies(db_connector=self.__db_connector,
                                                    **self.__default_validation_parameters_level['app'],
                                                    **self.__default_validation_parameters_level['connection'])
        logger.info("Services: Successfully Read Active Companies")

        return php_active_companies

    def find_active_companies(self) -> tuple:
        """
        Find active companies based on analytics algorithm
        :return: Dataframe with company info
        """
        # Get active
        cnc = OliverClassifierTimeSeries(api_sources_fetcher=self.__api_data_fetcher)

        logger.info("OliverClassifier: Successfully Set Parameters")

        alg_active_companies, last_year, last_week = cnc.identify_active_companies()
        logger.info("OliverClassifier: Sucessfully Identified Active Companies")
        return alg_active_companies, last_year, last_week

    def identify_company_labels(self, analytics_active_companies: pd.DataFrame,
                                php_active_companies: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates ConfusionMatrixLabel
        :return: DataFrame containing the labels between the results from both algorithms
        :param analytics_active_companies active companies from analytics algorithm
        :param php_active_companies active companies from php algorithm
        """
        all_companies = self.__api_data_fetcher.get_companies_info(
            companies_columns_names=['id', 'name', 'domain', 'created_at', 'language', 'is_enabled', 'deleted_at'])

        labels = ConfusionMatrixLabel.active_companies(all_companies=all_companies,
                                                       true_companies=analytics_active_companies,
                                                       selected_companies=php_active_companies,
                                                       **self.__default_validation_parameters_level['labels'])
        logger.info("ConfusionMatrixLabel: Sucessfully labeled Active Companies")
        return labels

    def verify_accuracy(self, labels: pd.DataFrame) -> float:
        """
        Calculates accuracy based on labels
        :return: DataFrame containing the labels between the results from both algorithms
        :param labels labels resulting from analytics and php algorithms
        """
        accuracy = Evaluation.accuracy(labels, **self.__default_validation_parameters_level['labels'])
        logger.info("Evaluation: Accuracy Determined")
        return accuracy

    def check_active_companies(self):
        """
        Process active companies and return both DataFrames
        :return:
        """
        job_successfull = True
        message_heading = 'Successful Pipeline Execution - Implementation well done'
        last_year = 0
        last_week = 0
        accuracy = 0
        labels = pd.DataFrame
        try:
            php_act_companies = self.get_php_active_companies()

            if php_act_companies.empty:
                raise ValueError("Empty PHP active companies")

            analytics_act_companies, last_year, last_week = self.find_active_companies()
            labels = self.identify_company_labels(analytics_active_companies=analytics_act_companies,
                                                  php_active_companies=php_act_companies)
            accuracy = self.verify_accuracy(labels=labels)

            if accuracy != 100:
                job_successfull = False
                logger.warning("Implementation with errors: The accuracy is not 100")
                message_heading = 'Successful Pipeline Execution - Errors Found on Implementation'
            else:
                logger.info("Implementation Successfully Validated: Accuracy = 100%")

        except Exception as e:
            job_successfull = False
            message_heading = str(e)

        if not job_successfull and not labels.empty:
            log_active_company(self.__db_connector, last_week, last_year, accuracy, labels,
                               "Error: %s" % message_heading,
                               **self.__default_validation_parameters_level['labels'],
                               **self.__default_validation_parameters_level['validation'],
                               **self.__default_validation_parameters_level['connection'])

        if self.__default_validation_parameters_level['common']['alert']:
            # TODO: Redo this notification logic having in mind a notification listener and dispatcher
            # log_file = open("%s/engage-analytics.log" % get_project_path(), 'r').readlines()

            msg = generate_slack_message(message_heading=message_heading,
                                         status=job_successfull,
                                         logging_message="")
            AlertMessage.send_slack_message("Active Companies Workflow", msg)
