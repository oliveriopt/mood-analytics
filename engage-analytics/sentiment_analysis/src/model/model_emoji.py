import sentiment_analysis.src.model.cons as cons


class ModelEmoji:

    def __init__(self, text: str, sentiment: str):
        self.__text = text
        self.__sentiment = sentiment

    @staticmethod
    def __count_positives(cleaned_text: str) -> int:
        """
        Return number of positive emoji is in string
        :param cleaned_text:: text to analyze
        :return:
        """
        return len([item for item in cons.emojis_positives if item in cleaned_text.split()])

    @staticmethod
    def __count_negatives(cleaned_text: str) -> int:
        """
        Return number of negative emoji is in string
        :param cleaned_text:: text to analyze
        :return:
        """
        return len([item for item in cons.emojis_negatives if item in cleaned_text.split()])

    def __negative_sentiment(self, cleaned_text: str) -> bool:
        return self.__count_negatives(cleaned_text) > self.__count_positives(cleaned_text)

    def __positive_sentiment(self, cleaned_text: str) -> bool:
        return self.__count_positives(cleaned_text) > self.__count_negatives(cleaned_text)

    @staticmethod
    def __replace_characters(text) -> str:
        """
        Replace comma and point with spaces
        :return:
        """
        text = text.replace(",", " ")
        text = text.replace(".", " ")
        text = text.replace("\"", " ")
        text = text.replace("'", " ")

        return text

    def detect_emoji_sentiment(self) -> str:
        """
        Measures the number of emojis and classify the string as a function of the emojis
        :return: Sentiment
        """

        cleaned_text = self.__replace_characters(text=self.__text)

        if self.__negative_sentiment(cleaned_text):
            return "negative"
        elif self.__positive_sentiment(cleaned_text):
            return "positive"

        return self.__sentiment
