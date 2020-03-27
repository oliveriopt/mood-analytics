#!/usr/bin/env python3
import pymysql
import logging
import warnings
import sys
from utils.utilities import is_dev_env
import time

from utils.alerts.manager import NotificationManager

logger = logging.getLogger()
warnings.filterwarnings("ignore", category=pymysql.Warning)


class Connector:

    def __init__(self, user: str, pw: str, host: str, port=3306, database: str = None):
        assert user, "Database <user> is not set."
        assert host, "Database <host> is not set."
        assert port, "Database <port> is not set."

        self.__host = host
        self.__user = user
        self.__port = int(port)
        self.__password = pw
        self.__database = database
        self.__conn = None

    def close_connection(self):
        """
        Close connection to the database
        :return:
        """
        if self.__conn is not None:
            self.__conn.close()

    def open_connection(self) -> None:
        """
        Open a connection to MySQL server
        :return:
        """
        try:
            if self.__database:
                self.__conn = pymysql.connect(host=self.__host, port=self.__port,
                                              user=self.__user, passwd=self.__password, db=self.__database)
            else:
                self.__conn = pymysql.connect(host=self.__host, port=self.__port,
                                              user=self.__user, passwd=self.__password)
            logger.info(msg="Connection to server successful!")
        except Exception as e:
            logger.error(msg="Error connecting to database:  %s" % e)
            NotificationManager.notify_logging_event()
            sys.exit(1)

    def select_query(self, query: str) -> tuple:
        """
        Executes a SELECT query
        :return: object containing results from SELECT
        """
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(query)
                self.__conn.commit()
                result = cursor.fetchall()

        except Exception as e:
            logger.error(msg="Error executing select query: %s" % e)
            raise Exception('Not able to execute the select query %s : %s' % (query, e))

        return result

    def insert_query(self, query: str) -> int:
        """
        Executes a INSERT query
        :param query:
        :return: affected rows
        """
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(query)
                self.__conn.commit()
                return cursor.rowcount

        except Exception as e:
            logger.error(msg="Error executing insert query: %s" % e)
            raise Exception('Not able to execute the select query %s : %s' % (query, e))
