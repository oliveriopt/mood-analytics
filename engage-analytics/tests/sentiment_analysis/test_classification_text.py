import sentiment_analysis.src.constants as global_cons

from unittest import TestCase
from sentiment_analysis.src.model.labelling_interface import InterfaceLabel


class TestInterfaceLabel(TestCase):

    def test_label_sentiment_neutral(self):
        score = 0.1
        thresholds = (-0.2, 0.2)
        sentiment = InterfaceLabel.label_sentiment(score, thresholds)
        assert sentiment == global_cons.NEUTRAL
        self.assertIsInstance(sentiment, str)

    def test_label_sentiment_positive(self):
        score = 0.2
        thresholds = (-0.2, 0.2)
        sentiment = InterfaceLabel.label_sentiment(score, thresholds)
        assert sentiment == global_cons.POSITIVE
        self.assertIsInstance(sentiment, str)

    def test_label_sentiment_negative(self):
        score = -0.4
        thresholds = (-0.2, 0.2)
        sentiment = InterfaceLabel.label_sentiment(score, thresholds)
        assert sentiment == global_cons.NEGATIVE
        self.assertIsInstance(sentiment, str)
