import numpy as np
import sentiment_analysis.src.constants as global_cons

from sentiment_analysis.src.model.positiveness_negativeness import PositivenessNegativeness


class BuildHistogram:

    def __init__(self, sentiment_text: str, splitted_word: list, freq_norm: dict, difference_pos: list,
                 difference_neg: list, calibrate=bool):
        self.sentiment_text = sentiment_text
        self.splitted_word = splitted_word
        self.freq_norm = freq_norm
        self.difference_pos = difference_pos
        self.difference_neg = difference_neg
        self.bin_edges_pos = []
        self.bin_edges_neg = []
        self.mean_pos = 0
        self.mean_neg = 0
        self.calibrate = calibrate

    def __stack_value_difference(self) -> None:
        """
        Stack the new value of difference in the list
        :return:
        """

        if self.sentiment_text == global_cons.POSITIVE:
            self.difference_pos.append(PositivenessNegativeness().calculate_difference(splitted_word=self.splitted_word,
                                                                                       freq_norm=self.freq_norm))
        else:
            self.difference_neg.append(PositivenessNegativeness().calculate_difference(splitted_word=self.splitted_word,
                                                                                       freq_norm=self.freq_norm))

    def __calculate_mean_std(self) -> None:
        """
        Calculate the values of the histogram
        :return:
        """

        self.hist_pos, self.bin_edges_pos = np.histogram(self.difference_pos, density=True)
        self.hist_neg, self.bin_edges_neg = np.histogram(self.difference_neg, density=True)
        self.mean_pos = np.average(a=self.bin_edges_pos[:-1], axis=None, weights=self.hist_pos[:], returned=False)
        self.mean_neg = np.average(a=self.bin_edges_neg[:-1], axis=None, weights=self.hist_neg[:], returned=False)

    def run_histogram(self) -> None:
        """
        Run the class
        :return:
        """
        if self.calibrate:
            self.__stack_value_difference()
            self.__calculate_mean_std()

        else:
            self.__calculate_mean_std()
