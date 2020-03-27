import os

from utils.data_connection.redis_manager import RedisManager


class RedisFactory:

    @staticmethod
    def build() -> RedisManager:
        """
        Factory for Redis
        :return: RedisManager
        """
        redis = RedisManager(host=os.getenv("REDIS_HOST"),
                             port=os.getenv("REDIS_PORT"),
                             db=os.getenv("REDIS_DB"))

        redis.open_client()

        return redis
