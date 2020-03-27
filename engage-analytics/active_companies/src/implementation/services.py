"""
Modules to get active companies from DB 
"""
import os
import pandas as pd
import logging
import utils.data_connection.constant_variables_db as cons

from utils.data_connection.source_manager import Connector
from utils.utilities import get_today_year_week

logger = logging.getLogger()


def get_active_companies(db_connector: Connector, **db_parameter: dict) -> pd.DataFrame:
    """
    Get All Active Companies from the mood_insights
    :param db_connector Connector to DB server
    :param db_parameter parameters to use
    :return: data_connection frame with active companies
    """
    db_parameter_default = {
        'user': os.getenv("DB_USER"),  # user to connect to the database
        'pwd': os.getenv("DB_PASSWORD"),  # password to connect to the database
        'host': os.getenv("DB_HOST"),  # host/ip to connect to the database
        'database': os.getenv("INSIGHTS_DB_NAME"),  # name of the schema or database to connect
        'port': os.getenv("DB_PORT"),  # port number
        'columns': cons.ACTIVE_COMPANIES_COLUMNS,  # List with the columns names of the table with active names
        'table': "%s.%s" % (os.getenv("INSIGHTS_DB_NAME"), cons.ACTIVE_COMPANIES_TABLE)
        # name of the table with active names
    }

    # Check required keys
    required_keys = db_parameter_default.keys()
    fail_keys = [k for k in db_parameter.keys() if k not in required_keys]
    if fail_keys:
        logger.error("Services: The keys {keys!r} are not the required".format(keys=fail_keys))
        raise TypeError("The keys {keys!r} are not the required".format(keys=fail_keys))

    db_parameter_default.update(db_parameter)

    # build the query
    try:
        today_year, today_week = get_today_year_week()
        query = "SELECT %s FROM %s WHERE year=%s AND week=%s ;" % (",".join(db_parameter_default.get('columns')),
                                                                   "%s.%s" % (os.getenv("INSIGHTS_DB_NAME"),
                                                                              db_parameter_default.get('table')),
                                                                   today_year,
                                                                   today_week)

        db_connector.open_connection()

        result = db_connector.select_query(query)

        if len(result) > 0:
            php_active_company_ids = result[0][0].split(",")

            df = pd.DataFrame(php_active_company_ids, columns=["company_id"])

        else:
            logger.error(msg="Services: Active Companies Table Empty from PHP Code")
            df = pd.DataFrame([], columns=["company_id"])

        logger.info(msg="Services: Successfully Get Active Companies")
        db_connector.close_connection()

    except Exception as e:
        db_connector.close_connection()
        logger.error(msg="Error on Validation db: %s" % e)
        raise Exception(e)

    return df
