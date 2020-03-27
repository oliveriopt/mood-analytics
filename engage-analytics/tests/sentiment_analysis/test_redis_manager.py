import json
import os

from utils.data_connection.redis_manager import RedisManager
from unittest import TestCase, mock


class TestRedisManager(TestCase):
    @mock.patch.dict(os.environ, {"REDIS_DB": "5"})
    @mock.patch.dict(os.environ, {"REDIS_HOST": "127.0.0.1"})
    @mock.patch.dict(os.environ, {"REDIS_PORT": "6379"})
    def setUp(self):
        self.redis_manager = RedisManager(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"),
                                          os.getenv("REDIS_DB"))
        self.week_analyze = [[29, 2019], [30, 2019]]
        self.base_period = "%s_%s" % (self.week_analyze[0][0], self.week_analyze[0][1])
        self.company_id = "xpto-xpto-xpto-xpto"
        self.dict_test = {"8abcf6e2-f7e0-45db-9691-51eae607fb41":
                              {"text": "Happy Birthday Ted ",
                               "score": "-0.30000",
                               "entities_text": ["work"],
                               "entities_type": ["OTHER"]},
                          "d6a37bf8-3785-44af-a1bd-8dcc19a8c61e":
                              {"text": "Happy Birthday Ted ",
                               "score": "-0.30000001192092896",
                               "entities_text": ["work"],
                               "entities_type": ["OTHER"]},
                          "f1cad55b-c6fb-4ffb-920c-461f74159eb1":
                              {"text": "Happy Birthday Ted ",
                               "score": "-0.30000001192092896",
                               "entities_text": ["work"],
                               "entities_type": ["OTHER"]}}
        self.dict_test_retrieve = json.dumps({"8abcf6e2-f7e0-45db-9691-51eae607fb41":
                                                  {"text": "Happy Birthday Ted ",
                                                   "score": "-0.30000",
                                                   "entities_text": ["work"],
                                                   "entities_type": ["OTHER"]},
                                              "d6a37bf8-3785-44af-a1bd-8dcc19a8c61e":
                                                  {"text": "Happy Birthday Ted ",
                                                   "score": "-0.30000001192092896",
                                                   "entities_text": ["work"],
                                                   "entities_type": ["OTHER"]},
                                              "f1cad55b-c6fb-4ffb-920c-461f74159eb1":
                                                  {"text": "Happy Birthday Ted ",
                                                   "score": "-0.30000001192092896",
                                                   "entities_text": ["work"],
                                                   "entities_type": ["OTHER"]}})

    def tearDown(self):
        del self.redis_manager, self.company_id, self.dict_test

    @mock.patch("utils.data_connection.redis_manager.redis.StrictRedis.hget", autospec=True)
    @mock.patch("utils.data_connection.redis_manager.redis.StrictRedis.hset", autospec=True)
    def test_persist_retrieve(self, mock_redis_hset, mock_redis_hget):
        mock_redis_hset.return_value = self.dict_test
        mock_redis_hget.return_value = self.dict_test_retrieve

        self.redis_manager.open_client()

        self.redis_manager.persist(self.company_id, self.base_period, self.dict_test)
        result = self.redis_manager.retrieve(self.company_id, self.base_period)

        assert self.dict_test == result

    def test_exception_persist(self):
        self.redis_manager.open_client()
        self.assertRaises(Exception, self.redis_manager.persist(self.company_id, self.base_period, self.dict_test))

    def test_exception_retrieve(self):
        self.redis_manager.open_client()
        self.assertRaises(Exception, self.redis_manager.retrieve(self.company_id, self.base_period))

    def test_not_exception_persist(self):
        self.redis_manager.open_client()
        raised = False
        try:
            self.redis_manager.persist(self.company_id, self.base_period, self.dict_test)
        except:
            raised = True
        self.assertFalse(raised, "Error inserting the info into Redis for company = %s" % self.company_id)

    def test_not_exception_retrieve(self):
        self.redis_manager.open_client()
        raised = False
        try:
            result = self.redis_manager.retrieve(self.company_id, self.base_period)
        except:
            raised = True
        self.assertFalse(raised, "Error inserting the info into Redis for company = %s" % self.company_id)
        self.assertIsInstance(result, dict)
        self.assertIsNot(result, None)
