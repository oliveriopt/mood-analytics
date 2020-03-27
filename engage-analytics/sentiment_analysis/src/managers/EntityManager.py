import logging
from collections import defaultdict

import sentiment_analysis.src.constants as cons
from sentiment_analysis.src.model.model_sa import ModelsSentimentAnalysis
from utils.stanford.ner_tagger import StfNERTagger

from utils.data_connection.api_data_manager import APISourcesFetcher
from sentiment_analysis.src.clean_comments import CleanComments
from google.cloud.language_v1 import LanguageServiceClient
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from utils.data_connection.redis_manager import RedisManager

logger = logging.getLogger()


class EntityManager:
    """
    Manager for all operations on survey_replies
    """

    def __init__(self, api_manager: APISourcesFetcher, period: dict,
                 google_client: LanguageServiceClient, redis_manager: RedisManager, company_ids: list):
        self.__period = period
        self.__company_ids = company_ids
        self.__api_data_fetcher = api_manager
        self.__st_ner_tagger = StfNERTagger()
        self.__models = {}
        self.__google_client = google_client
        self.__redis = redis_manager
        self._process_prefix = True
        self._result = defaultdict(lambda: defaultdict(dict))
        self._data = None

    @property
    def company_ids(self) -> list:
        """
        Return list of company_ids
        :return:
        """
        return self.__company_ids

    @property
    def period(self) -> dict:
        """
        Return period
        :return:
        """
        return self.__period

    @property
    def api_manager(self) -> APISourcesFetcher:
        """
        Return api manager
        :return:
        """
        return self.__api_data_fetcher

    def get_results(self) -> dict:
        """
        Return results from processing
        :return: dict containing all results processed
        """
        return self._result

    def fetch_data(self) -> None:
        """
        Fetches data from sources
        """
        pass

    def _clean_comments(self, comment: str, filter_stopwords: bool = False) -> str:
        """
        Procedure to clean and beautify the comment
        :param comment: comment to analyze
        :param filter_stopwords: bool to filter stopwords or not
        :return:
        """
        text = CleanComments.decode_html_entities(comment=comment)
        text = CleanComments.filter_urls(comment=text)
        text = CleanComments.strip_emojis(comment=text)
        text = CleanComments.filter_spaces(comment=text)
        text = CleanComments.filter_words_without_numbers(comment=text)
        text = CleanComments.filter_special_chars_surrounded_spaces(comment=text)

        if filter_stopwords:
            language, __ = ClientsLanguageSentiment.dominant_language_sentiment_text(self.__google_client, text)

            if (language == cons.lang_german) or (language == cons.lang_english):
                text = CleanComments.filter_stopwords(language, text)
            else:
                text = None

        return text

    def _process_sentiment(self, company_id: str, text: str) -> tuple:
        """
        Process score sentiment
        :param company_id: id of the company
        :param text: comment
        :return: score and sentiment of the text
        """

        model_sa = self.__models.get(company_id)

        if not model_sa:
            model_sa = ModelsSentimentAnalysis(company_id=company_id,
                                               redis=self.__redis)
            self.__models[company_id] = model_sa

        result = model_sa.predict(text=text)

        return result.get("score"), result.get("sentiment")

    def _process_entities(self, text: str) -> tuple:
        """
        Process entities sentiment
        :param text: comment
        :return: return entities text and types
        """

        entities_text, __, entities_type = ClientsLanguageSentiment.dominant_entities_text(
            stanford_client=self.__st_ner_tagger,
            client_google=self.__google_client, comment=text)

        # Final filter on the entities to ensure no noise is introduced in the entities
        entities_text = [CleanComments.filter_special_characters(comment=entity).strip() for entity in entities_text]

        return entities_text, entities_type
