import logging

from utils.utilities import get_project_path
from nltk.tag.stanford import StanfordNERTagger
from sentiment_analysis.src.clean_comments import CleanComments

logger = logging.getLogger()


class StfNERTagger:

    def __init__(self):
        """
        Open client for Stanford NERTagger
        :return: protocol open
        """

        ser_path = get_project_path() + '/nltk_libs/english.all.3class.distsim.crf.ser'
        jar_path = get_project_path() + '/nltk_libs/stanford-ner-3.8.0.jar'

        self.st = StanfordNERTagger(ser_path, jar_path)

    def identify_person_types(self, text: str) -> list:
        """
        Users Stanford NERTagger to identify person types. It cleans-up some unwanted chars to have better accuracy
        :param text: text to identify types
        :return: list
        """
        cleaned_text = CleanComments.filter_special_characters(comment=text)

        words = cleaned_text.strip().split()
        tags = []

        try:
            tags = self.st.tag(words)
        except Exception as e:
            logger.warning(msg="Error identifying entities using Stanford: %s " % str(e))

        return [tag[0].lower() for tag in tags if tag[1] == "PERSON"]
