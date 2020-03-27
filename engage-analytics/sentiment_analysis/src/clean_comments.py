import html
import re
import sentiment_analysis.src.constants as cons
import nltk

nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords


class CleanComments:

    @staticmethod
    def decode_html_entities(comment: str) -> str:
        """
        Decode report_html entities using unscape
        :param comment: text to decode the report_html entities
        :return: text already decode
        """
        comment = html.unescape(comment)

        return comment

    @staticmethod
    def filter_special_characters(comment: str) -> str:
        """
        Fiter special character and convert into lower characters
        :param comment: text to convert
        :return: text already filtered and converted
        """
        # Removes punctuation except for apostrophes AND intra-word dashes
        # Additionally preserves german chars
        result = re.sub("[^a-zA-Z^äöüÄÖÜßãíáéóÂÍçÊ'-]|['-]{2,}", " ", comment)

        return result

    @staticmethod
    def filter_words_without_numbers(comment: str) -> str:
        """
        Filters all words that have no numbers
        :param comment: text to convert
        :return:
        """
        result = re.sub(r"\d{1,2}[,.]\d{1,2}|\d", "", comment)
        return result

    @staticmethod
    def filter_spaces(comment: str) -> str:
        """
        Filters all spaces to a single space
        :param comment: text to convert
        :return:
        """
        result = re.sub("[\r\n\t\s]+", " ", comment)
        return result

    @staticmethod
    def filter_special_chars_surrounded_spaces(comment: str) -> str:
        """
        Filters all characters that are surrounded with spaces
        :param comment: text to convert
        :return:
        """
        result = re.sub('\s[!@#$%^&*(),.?":+{}|<>\/-]\s', " ", comment)
        return result

    @staticmethod
    def filter_urls(comment: str) -> str:
        """
        Fiter urls from the text
        :param comment: text to convert
        :return: text already filtered and converted
        """
        comment = re.sub(r'http\S+', '', comment)

        return comment.lower()

    @staticmethod
    def filter_stopwords(language: str, comment: str) -> str:
        """
        Filter of the stop words. Depending of the language and keep the negative stop words in the comment
        :param language: german or english language
        :param comment: text to filter the stop words
        :return: text without the stopwords
        """

        if language == cons.lang_english:
            lang = "english"
            stop = set(stopwords.words(lang)) - set(cons.stop_words_negatives_english)
        elif language == cons.lang_german:
            lang = "german"
            stop = set(stopwords.words(lang)) - set(cons.stop_words_negatives_german)

        comment = [i for i in comment.split() if i not in stop]
        comment = ' '.join(str(e) for e in comment)

        return comment

    @staticmethod
    def strip_emojis(comment: str) -> str:
        """
        Remove emojis and emoticons from text
        :param comment:
        :return:
        """
        emoticon_filtered = re.sub(
            ":\)|:-\)|:\(|:-\(|;\);-\)|;-\)|;-p|:d|:-O|<3|8-|:P|:D|:\||:S|:\$|:@|8o\||\+o\(|\(H\)|\(C\)|\(\?\)", "",
            comment)
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', emoticon_filtered)
