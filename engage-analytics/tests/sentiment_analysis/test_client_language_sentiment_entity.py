import numpy as np

from google.cloud.language import enums
from google.cloud.language import types
from unittest import TestCase
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from sentiment_analysis.src.model.labelling_interface import InterfaceLabel
from utils.stanford.ner_tagger import StfNERTagger
from utils.gcloud.nlp_client import NLPGoogleClient
import sentiment_analysis.src.constants as global_cons


class TestClientsLanguageSentiment(TestCase):

    def setUp(self):
        self.text = "Convert the comment into a google document type"
        self.stf_ner_tagger = StfNERTagger()
        self.g_client = NLPGoogleClient.open_client()
        self.document = types.Document(
            content=self.text,
            type=enums.Document.Type.PLAIN_TEXT)

        self.scores = [1, 2, 3, 4, 5, 6, np.nan]
        self.company_id = "xpto-xpto-xpto-xpto"
        self.thresholds = (-0.1, 0.5)
        self.test_scores = [-0.30000001192092896, -0.30000001192092896, -0.30000001192092896, 0.800000011920929,
                            0.800000011920929, 0.800000011920929, 0.10000000149011612, 10000000149011612,
                            10000000149011612]
        self.dict_test = {"xpto-xpto-xpto-xpto": {'29_2019':
                                                      {'8abcf6e2-f7e0-45db-9691-51eae607fb41':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']},
                                                       'd6a37bf8-3785-44af-a1bd-8dcc19a8c61e':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']},
                                                       'f1cad55b-c6fb-4ffb-920c-461f74159eb1':
                                                           {'text': 'Happy Birthday Ted ',
                                                            'score': -0.30000001192092896,
                                                            'entities_text': ['work'],
                                                            'entities_type': ['OTHER']}},
                                                  '30_2019':
                                                      {'45224527-7137-4451-b747-40e25f4ff146':
                                                          {
                                                              'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                              'score': 0.800000011920929,
                                                              'entities_text': ['manager', 'team lead', 'boss'],
                                                              'entities_type': ['PERSON', 'OTHER', 'PERSON']},
                                                          'aa98f181-6078-441f-a117-613daf2b8502':
                                                              {
                                                                  'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                                  'score': 0.800000011920929,
                                                                  'entities_text': ['manager', 'team lead', 'boss'],
                                                                  'entities_type': ['PERSON', 'OTHER', 'PERSON']},
                                                          'b9d51ac3-2d7e-44c1-8c03-9846712de99f':
                                                              {
                                                                  'text': 'Even though Rahima is just our interim "boss", couldn\'t imagine a more motivating team lead!',
                                                                  'score': 0.800000011920929,
                                                                  'entities_text': ['manager', 'team lead', 'boss'],
                                                                  'entities_type': ['PERSON', 'OTHER', 'PERSON']}},
                                                  '31_2019':
                                                      {'c8cfca75-c92e-4d7d-adb8-8210ce693e78':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []},
                                                       '6f60e2bd-84b7-402c-87ff-6e7508e6f34f':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []},
                                                       '2ed90395-56d2-41e7-a0da-fe5d5514c2e1':
                                                           {'text': 'I can leave on time but ',
                                                            'score': 0.10000000149011612,
                                                            'entities_text': [],
                                                            'entities_type': []}
                                                       }
                                                  }
                          }
        self.dict_filter = {"key": 0.3,
                            "kei": 0.1,
                            "key1": 5,
                            "key2": 5,
                            "thing": 1,
                            "things": 3
                            }

    def TearDown(self):
        del self.document, self.scores
        del self.dict_test, self.company_id, self.dict_filter

    def test_convert_type_google_document(self):
        doc_test = ClientsLanguageSentiment.convert_type_google_document(self.text)

        assert doc_test == self.document
        assert type(doc_test) == type(self.document)

    def test_calculate_threshold_positive_negative(self):
        TestClientsLanguageSentiment.setUp(self)
        thrs = InterfaceLabel.calculate_threshold_positive_negative(self.test_scores)

        assert thrs == (-1935174903029620.8, 6379619413701448.0)
        TestClientsLanguageSentiment.TearDown(self)

    def test_count_entities(self):
        TestClientsLanguageSentiment.setUp(self)
        entities_text = ClientsLanguageSentiment.count_entities(
            [["work", "manager", "team lead", "boss"],
             ["work", "manager", "team lead", "boss"],
             ["work", "manager", "team lead", "boss"]])
        assert entities_text["work"] == 3
        assert entities_text["manager"] == 3
        assert entities_text["team lead"] == 3
        assert entities_text["boss"] == 3
        TestClientsLanguageSentiment.TearDown(self)

    def test_filter_blacklist_keys_dict(self):
        counter = ClientsLanguageSentiment.filter_black_list(self.dict_filter)
        assert counter == {'key': 0.3, 'kei': 0.1, 'key1': 5, 'key2': 5}

    def test_filter_blacklist_keys_list(self):
        keys_list = [key for key, val in self.dict_test.items()]
        counter = ClientsLanguageSentiment.filter_black_list(keys_list)
        assert counter == keys_list

    def test_dominant_entities_text(self):
        entities_google_text, entities_google_salience, entities_google_type = ClientsLanguageSentiment.dominant_entities_text(
            stanford_client=self.stf_ner_tagger, client_google=self.g_client,
            comment="Tomorrow I will say John is the most valuable team member from Vienna")

        self.assertIsInstance(entities_google_text, list)
        self.assertIsInstance(entities_google_salience, list)
        self.assertIsInstance(entities_google_type, list)

        assert entities_google_text == ["Vienna"]
        assert len(entities_google_salience) > 0
        assert entities_google_type == ["LOCATION"]

    def test_dominant_entities_text_empty(self):
        entities_google_text, entities_google_salience, entities_google_type = ClientsLanguageSentiment.dominant_entities_text(
            stanford_client=self.stf_ner_tagger, client_google=self.g_client,
            comment="")

        self.assertIsInstance(entities_google_text, list)
        self.assertIsInstance(entities_google_salience, list)
        self.assertIsInstance(entities_google_type, list)

        assert entities_google_text == []
        assert entities_google_salience == []
        assert entities_google_type == []

    def test_dominant_entities_text_mismatch_person_type(self):
        entities_google_text, entities_google_salience, entities_google_type = ClientsLanguageSentiment.dominant_entities_text(
            stanford_client=self.stf_ner_tagger, client_google=self.g_client,
            comment="António is great")

        self.assertIsInstance(entities_google_text, list)
        self.assertIsInstance(entities_google_salience, list)
        self.assertIsInstance(entities_google_type, list)

        assert entities_google_text == ["António"]
        assert len(entities_google_salience) > 0
        assert entities_google_type == ["PERSON"]

    def test_dominant_entities_text_no_person_type(self):
        entities_google_text, entities_google_salience, entities_google_type = ClientsLanguageSentiment.dominant_entities_text(
            stanford_client=self.stf_ner_tagger, client_google=self.g_client,
            comment="Agathe")

        self.assertIsInstance(entities_google_text, list)
        self.assertIsInstance(entities_google_salience, list)
        self.assertIsInstance(entities_google_type, list)

        assert entities_google_text == []
        assert entities_google_salience == []
        assert entities_google_type == []

    def test_label_sentiment_positive(self):
        TestClientsLanguageSentiment.setUp(self)
        score = 0.51
        sentiment = InterfaceLabel.label_sentiment(score=score, thresholds=self.thresholds)
        assert sentiment == global_cons.POSITIVE
        self.assertIsInstance(sentiment, str)

    def test_label_sentiment_negative(self):
        TestClientsLanguageSentiment.setUp(self)
        score = -0.51
        sentiment = InterfaceLabel.label_sentiment(score=score, thresholds=self.thresholds)
        assert sentiment == global_cons.NEGATIVE
        self.assertIsInstance(sentiment, str)

    def test_label_sentiment_neutral(self):
        TestClientsLanguageSentiment.setUp(self)
        score = 0.2
        sentiment = InterfaceLabel.label_sentiment(score=score, thresholds=self.thresholds)
        assert sentiment == global_cons.NEUTRAL
        self.assertIsInstance(sentiment, str)
