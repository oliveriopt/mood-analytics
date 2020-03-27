import unittest

from sentiment_analysis.src.model.frequency_words import FrequencyWords


class TestFrequencyWords(unittest.TestCase):

    def setUp(self):
        self.sentiment = "positive"
        self.freq = {"word": {"positive": 1, "neutral": 2, "negative": 1},
                     "best": {"positive": 1, "neutral": 1, "negative": 0}}
        self.splitted_words = ["kununu", "action", "best"]

    def tearDown(self):
        del self.sentiment
        del self.freq
        del self.splitted_words

    def test_calibrate_frequency_positive(self):
        frequency = FrequencyWords(self.sentiment, self.freq, self.splitted_words)

        frequency.calibrate_frequency(calibrate_neutral=True)
        assert frequency.freq == {'word': {'positive': 1, 'neutral': 2, 'negative': 1},
                                  'best': {'positive': 0, 'neutral': 1, 'negative': 0},
                                  'kununu': {'positive': 1, 'neutral': 0, 'negative': 0},
                                  'action': {'positive': 1, 'neutral': 0, 'negative': 0}}
        self.assertIsInstance(frequency.freq, dict)

    def test_norm_dict_freq(self):
        frequency = FrequencyWords(self.sentiment, self.freq, self.splitted_words)
        norm = frequency.norm_dict_freq(self.freq)
        assert norm == {
            'word': {'positive': 16.666666666666664, 'neutral': 33.33333333333333, 'negative': 16.666666666666664},
            'best': {'positive': 16.666666666666664, 'neutral': 16.666666666666664, 'negative': 0.0}}
        self.assertIsInstance(norm, dict)

    def test_count_words(self):
        frequency = FrequencyWords(self.sentiment, self.freq, self.splitted_words)
        count = frequency.count_words(self.freq)
        assert count == 6
        self.assertIsInstance(count, int)
