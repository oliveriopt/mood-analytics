import redis
import json
import logging
import sys

logger = logging.getLogger()


class RedisManager:

    def __init__(self, host: str = "127.0.0.1", port: int = 6379, db: int = 5):
        assert host, "Database Redis <redis_host> is not set."
        assert port, "Database <redis_port> is not set."
        assert db, "Database <redis_db> is not set."

        self.__connection_redis = None
        self.__host = host
        self.__port = port
        self.__database = db

    def open_client(self) -> None:
        """
        Open client in redis
        :return:
        """
        try:

            self.__connection_redis = redis.StrictRedis(host=self.__host,
                                                        port=self.__port,
                                                        db=self.__database,
                                                        charset="utf-8",
                                                        decode_responses=True).client()
            logger.info(msg="Connection to Redis server successful!")

        except Exception as e:
            logger.error(msg="Error connecting to Redis server:  %s" % e)
            sys.exit(1)

    def persist(self, key: str, field: str, data: dict, ) -> None:
        """
        Write the dict into redis server
        :param key: key string
        :param field: field string
        :param data: dict to persist in redis
        :return:
        """
        try:
            self.__connection_redis.hset(key, field, json.dumps(data))
            logger.info(msg="Persistence to Redis server successful for key = %s and field = %s" % (key, field))
        except Exception as e:
            logger.error(msg="Error inserting the info into Redis for key = %s and field = %s: %s" % (key, field, e))
            raise Exception("Error inserting the info into Redis for key = %s and field = %s: %s" % (key, field, e))

    def retrieve(self, key: str, field: str) -> object:
        """
        Convert bytes and string to dictionary
        :param key: key string
        :param field: field string
        :return: obj (value, list or dict)
        """

        try:
            logger.info(msg="Retrieving info from Redis server successful for key = %s and field = %s" % (key, field))
            result = json.loads(self.__connection_redis.hget(key, field))
        except Exception as e:
            logger.error(msg="Error retrieving the info on Redis for company = %s and field %s : %s" % (key, field, e))
            return {}
        return result
