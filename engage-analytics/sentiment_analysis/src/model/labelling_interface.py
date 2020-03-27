import logging
import sentiment_analysis.src.constants as global_cons

from scipy.stats import norm
from nested_lookup import nested_lookup

logger = logging.getLogger()


class InterfaceLabel:

    @staticmethod
    def label_sentiment(score: float, thresholds: tuple) -> str:
        """
        Label sentiment on interface
        :param score: score of the text
        :param thresholds: thresholds of negative and positive sentiment
        :return: sentiment label
        """
        sentiment = global_cons.NEUTRAL
        if score <= thresholds[0]:
            sentiment = global_cons.NEGATIVE
        if score >= thresholds[1]:
            sentiment = global_cons.POSITIVE

        return sentiment

    @staticmethod
    def calculate_threshold_positive_negative(scores: list) -> tuple:
        """
        Calculate the threshold for the given dict
        :param scores: list of scores stored in REDIS, resulting from previous classifications
        :return: threshold of positive and negative label
        """

        if not scores:
            logger.warning(msg="Empty baseline (scores) to calculate thresholds.")
            return None, None

        mu, std = norm.fit(scores)
        threshold_pos = mu + std
        threshold_neg = mu - std

        return threshold_neg, threshold_pos
