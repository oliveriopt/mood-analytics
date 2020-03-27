import copy
import sentiment_analysis.src.model.cons as cons
import sentiment_analysis.src.constants as global_cons

from nested_lookup import nested_lookup


class FrequencyWords:

    def __init__(self, sentiment: str, freq: dict, splitted_word: list):
        self.sentiment = sentiment
        self.freq = freq
        self.splitted_word = splitted_word

    def calibrate_frequency(self, calibrate_neutral: bool) -> None:
        """
        Update dictionary with the frequency after change the sentiment
        :return:
        """
        for item in self.splitted_word:
            if item in self.freq:
                value = self.freq.get(item).get(self.sentiment) + 1
                self.freq.get(item).update({self.sentiment: value})
                if calibrate_neutral:
                    value = self.freq.get(item).get(global_cons.NEUTRAL) - 1
                    self.freq.get(item).update({self.sentiment: value})
            else:
                self.freq.update({item: {global_cons.POSITIVE: 0,
                                         global_cons.NEUTRAL: 0,
                                         global_cons.NEGATIVE: 0}})
                value = self.freq.get(item).get(self.sentiment) + 1
                self.freq.get(item).update({self.sentiment: value})

    @staticmethod
    def norm_dict_freq(freq_dict: dict) -> dict:
        """
        Sorting dictionary of the frequency
        :param freq_dict: dictionary with the frequency of the words
        :return:
        """
        freq_norm = copy.deepcopy(freq_dict)
        length = FrequencyWords.count_words(freq_norm)

        if length > 0:
            for key in list(freq_norm.keys()):
                for sentiment in cons.sentiments:
                    value = (freq_norm.get(key).get(sentiment) / length) * 100
                    freq_norm.get(key).update({sentiment: value})
        return freq_norm

    @staticmethod
    def count_words(frequency: dict) -> int:
        """
        Count the population of words in the dict
        :param frequency: dictionary of words based on sentiments
        :return:
        """
        length = 0
        for key in list(frequency.keys()):
            temp = frequency[key]
            for i in cons.sentiments:
                length = length + sum(nested_lookup(i, temp))

        return length
