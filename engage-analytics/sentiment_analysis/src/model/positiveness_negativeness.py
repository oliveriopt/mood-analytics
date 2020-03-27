import sentiment_analysis.src.constants as global_cons


class PositivenessNegativeness:

    @staticmethod
    def calculate_ness(sentiment: str, splitted_word: list, frequency_nor: dict) -> float:
        """
        Calculate positiveness or negativeness of a list of words
        :param sentiment: sentiment to calculate weight
        :param splitted_words: list of words to analyze
        :param frequency_nor: dictionary with the normalised data
        :return:
        """
        weight = 0
        for key in splitted_word:
            if key in frequency_nor.keys():
                weight = weight + frequency_nor.get(key).get(sentiment)

        return round(weight, 2)

    @staticmethod
    def calculate_difference(splitted_word: list, freq_norm: dict) -> float:
        """
        Calculate positiveness/negativeness of a text suing the normalised dictionary
        :param splitted_word: list of words to analyze
        :param freq_norm: dictionary with the normalised data
        :return:
        """
        positiveness = PositivenessNegativeness().calculate_ness(sentiment=global_cons.POSITIVE,
                                                                 splitted_word=splitted_word,
                                                                 frequency_nor=freq_norm)

        negativeness = PositivenessNegativeness().calculate_ness(sentiment=global_cons.NEGATIVE,
                                                                 splitted_word=splitted_word,
                                                                 frequency_nor=freq_norm)

        return round(positiveness - negativeness, 2)
