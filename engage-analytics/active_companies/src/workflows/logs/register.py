"""
Script with modules to deal with logs and id for logs in multiple pipelines to insert to the database
"""

import logging
import os
import pandas as pd
import utils.data_connection.constant_variables_db as cons

from datetime import datetime
from utils.data_connection.source_manager import Connector
from utils.utilities import create_id

logger = logging.getLogger()


def log_active_company(db_connector: Connector, current_week: int, current_year: int, percent_accuracy: float,
                       labels: pd.DataFrame, error_msg: str = 'NULL', **log_parameters) -> None:
    """
        Function to add logs on the validation table for active companies validation on INSIGHTS DATABASE
        :param db_connector Connector for DB server
        :param current_week: current week on surveys
        :param current_year: current years
        :param percent_accuracy: accuracy between active companies on insights and from the OliverClassifier
        :param labels: data_connection frame with labels for each companies and source
        :param error_msg: error message if exists
        :param log_parameters: parameters to register logs
                List of parameters:
                    -> label_name_as_truth : name given to column of the data_connection frame labels we assume as the correct one
                    -> label_name_to_validate : name given to the columns of the data_connection frame label we as the one to
                    validate
                    -> table : name of the table we want to insert the log description
                    -> table_columns : list of the columns names from the defined table we want to insert values
                    -> table_detail : name of the table we want to insert the log details
                    -> table_detail_columns: list of the columns names from the defined table_details we want to insert
                    values
                    -> user: user to have access to the database,
                    -> password: password for the user to have access to the database
                    -> host: Ip address or domain for  the database,
                    -> database: name of the database
                    -> port: port number to access the database
        :return: None
        """

    default_settings = {
        "label_name_as_truth": 'label_true',
        "label_name_to_validate": 'label_algorithm',
        "table": cons.JOBS_ACTIVE_COMPANIES_TABLE,
        "table_columns": cons.JOBS_ACTIVE_COMPANIES_COLUMNS_NAMES,
        "table_detail": cons.JOBS_ACTIVE_COMPANIES_DETAILS_TABLE,
        "table_detail_columns": cons.JOBS_ACTIVE_COMPANIES_DETAILS_COLUMNS_NAMES,
        "user": os.getenv("DB_USER"),
        "pwd": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("INSIGHTS_DB_NAME"),
        "port": os.getenv("DB_PORT")
    }

    # Check required keys
    required_keys = default_settings.keys()
    fail_keys = [k for k in log_parameters.keys() if k not in required_keys]
    if fail_keys:
        raise TypeError("The {keys!r} are not the required".format(keys=fail_keys))

    # Update
    default_settings.update(log_parameters)

    # Check data_connection structures
    required_columns = ['id', default_settings.get('label_name_as_truth'),
                        default_settings.get('label_name_to_validate')]
    if list(labels.columns) == required_columns:
        raise Exception("labels doesn't the right columns {k!r}".format(k=required_columns))

    # Get log_id
    log_id = "\'%s\'" % create_id()

    # Get current date
    current_date = "\'%s\'" % str(datetime.now())

    if error_msg != 'NULL':
        error_msg = "\'%s\'" % error_msg

    # Create list with values to insert
    to_insert = [log_id, current_date, str(current_year), str(current_week), str(round(percent_accuracy, 2)),
                 error_msg]

    # "logs_active_company" query
    query_insert_log = "INSERT INTO %s ( %s ) VALUES ( %s )" % (
        "%s.%s" % (os.getenv("INSIGHTS_DB_NAME"), default_settings.get('table')),
        ",".join(default_settings.get('table_columns')),
        ",".join(to_insert))

    try:
        db_connector.open_connection()
        db_connector.insert_query(query_insert_log)

        # Cycle to insert the labels
        for row in labels.iterrows():
            # Get row values
            values = row[1]

            # Get id per company
            log_id_company = "\'%s\'" % create_id()

            # Create list with value to insert
            to_insert = [log_id_company, log_id, "\'" + values['id'] + "\'",
                         str(values[default_settings.get('label_name_as_truth')]),
                         str(values[default_settings.get('label_name_to_validate')])]

            # "logs_detail_active_company" query
            query_insert_log = "INSERT INTO %s ( %s ) VALUES ( %s )" % \
                               ("%s.%s" % (os.getenv("INSIGHTS_DB_NAME"), default_settings.get('table_detail')),
                                ",".join(default_settings.get('table_detail_columns')), ",".join(to_insert))
            db_connector.insert_query(query_insert_log)

        db_connector.close_connection()
    except Exception as e:
        raise Exception(e)
