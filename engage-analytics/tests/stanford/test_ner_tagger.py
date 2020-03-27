import unittest

from nltk import StanfordNERTagger

from utils.stanford.ner_tagger import StfNERTagger


class TestNERTagger(unittest.TestCase):

    def setUp(self):
        self.text = "Rami Eid John Maria João Rita José is a nice guy Fábio Anibal Steffen"

    def tearDown(self):
        del self.text

    def test_init_tagger(self):
        st_tagger = StfNERTagger()

        assert isinstance(st_tagger.st, StanfordNERTagger)

    def test_identify_person_types(self):
        st_tagger = StfNERTagger()

        result = st_tagger.identify_person_types(text=self.text)
        expected = ['rami', 'eid', 'john', 'maria', 'joão', 'rita', 'josé', 'fábio', 'anibal', 'steffen']

        assert isinstance(result, list)
        assert expected == result
