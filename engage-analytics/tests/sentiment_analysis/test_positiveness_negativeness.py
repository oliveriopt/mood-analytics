from sentiment_analysis.src.model.positiveness_negativeness import PositivenessNegativeness
from unittest import TestCase, mock

class TestPositivenessNegativeness(TestCase):

    def setUp(self):
        self.sentiment = "positive"
        self.norm = {
            'word': {'positive': 16.666666666666664, 'neutral': 33.33333333333333, 'negative': 16.666666666666664},
            'best': {'positive': 16.666666666666664, 'neutral': 16.666666666666664, 'negative': 0.0}}
        self.splitted_words = ["kununu", "action", "best"]
        self.poss_neg = PositivenessNegativeness()

    def tearDown(self):
        del self.sentiment
        del self.norm
        del self.splitted_words

    def test_calculate_poss_ness(self):
        weight = self.poss_neg.calculate_ness(self.sentiment, self.splitted_words, self.norm)
        assert weight == 16.67
        self.assertIsInstance(weight, float)

    @mock.patch('sentiment_analysis.src.model.positiveness_negativeness.PositivenessNegativeness.calculate_ness', autospec=True)
    def test_calculate_difference(self, mock_calculate_ness):
        mock_calculate_ness.return_value = 16.67
        diff = self.poss_neg.calculate_difference(self.splitted_words, self.norm)
        assert diff == 0.0
        self.assertIsInstance(diff, float)
