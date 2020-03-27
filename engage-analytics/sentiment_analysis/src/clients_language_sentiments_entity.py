import logging
import numpy as np
import collections
import sentiment_analysis.src.constants as cons
import truecase

from google.cloud.language import enums
from google.cloud.language import types
from utils.stanford.ner_tagger import StfNERTagger
from utils.utilities import extract_values_from_json

logger = logging.getLogger()


class ClientsLanguageSentiment:

    @staticmethod
    def convert_type_google_document(comment: str):
        """
        Convert the comment into a google document type
        :param comment: text to analyze
        :return: the google document type
        """
        document = types.Document(
            content=comment,
            type=enums.Document.Type.PLAIN_TEXT)
        return document

    @staticmethod
    def dominant_language_sentiment_text(client_google, comment: str) -> tuple:
        """
        Determine the dominant language using the method analyze_sentiment from google cloud
        :param client_google: connection to google cloud
        :param comment: text to analyze
        :return: the dominant language, german, english or others (cz)
        """
        dominant_language = ""
        score = np.nan
        if len(comment) > 0:
            try:
                document = ClientsLanguageSentiment.convert_type_google_document(comment)
                sentiment = client_google.analyze_sentiment(document=document)
                dominant_language = sentiment.language
                score = sentiment.document_sentiment.score
            except Exception as e:
                logger.error(msg=str(e))
                return None, np.nan
        return dominant_language, score

    @staticmethod
    def dominant_entities_text(stanford_client: StfNERTagger, client_google, comment: str) -> tuple:
        """
        Analyze the text and return the text entities and type entities
        :param stanford_client: connection to stanford client
        :param client_google: connection to google cloud
        :param comment: text to analyze
        :return: tuple with entities text and entitiies type
        """
        if len(comment) == 0:
            return [], [], []

        stf_person_types = stanford_client.identify_person_types(text=truecase.get_true_case(comment))

        document = ClientsLanguageSentiment.convert_type_google_document(comment)
        encoding = enums.EncodingType.UTF32
        entities_google_text = []
        entities_google_salience = []
        entities_google_type = []

        try:
            entities_google = client_google.analyze_entities(document, encoding).entities
            for entity in entities_google:
                entity_type = enums.Entity.Type(entity.type)

                # Discard low density words or high density words that can be related with an entity detection from google, leading to high density sentences
                if len(str(entity.name)) <= 3 or len(str(entity.name)) >= 25:
                    continue

                # Validates if Type.Person from GCloud is valid having Stanford as base line.
                # A lot of people names are not correctly detected by GCP but are from Stanford.
                if (entity_type == enums.Entity.Type.PERSON and entity.name.lower() in stf_person_types) or (
                        entity_type != enums.Entity.Type.PERSON and entity.name.lower() in stf_person_types) \
                        or entity_type in [enums.Entity.Type.NUMBER, enums.Entity.Type.PHONE_NUMBER,
                                           enums.Entity.Type.ADDRESS, enums.Entity.Type.PRICE, enums.Entity.Type.DATE]:
                    continue

                entities_google_text.append(entity.name)
                entities_google_salience.append(entity.salience)
                entities_google_type.append(entity_type.name)
            entities_google_text = list(entities_google_text)
            entities_google_salience = list(map(str, entities_google_salience))
            entities_google_type = list(set(entities_google_type))
        except Exception as e:
            logger.error(msg=str(e))
            return [], [], []
        return entities_google_text, entities_google_salience, entities_google_type

    @staticmethod
    def count_entities(entities: list, black_list_words: bool = True) -> dict:
        """
        Count number of entities text repeated
        :param entities: list of all entities
        :param black_list_words: if should blacklist some words
        :return:
        """
        single_list = [item for sublist in entities for item in sublist]

        if black_list_words:
            single_list = ClientsLanguageSentiment.filter_black_list(entities=single_list)

        counter = dict(collections.Counter(single_list))
        return counter

    @staticmethod
    def filter_black_list(entities) -> object:
        """
        Filter keys using blacklist
        :param entities: dictionary or list of entities tags
        :return:
        """
        if type(entities) is dict:
            entities = {key: entities[key] for key in entities if key not in cons.BLACKLIST_ENTITIES_TEXT}
        elif type(entities) is list:
            entities = [x for x in entities if x not in cons.BLACKLIST_ENTITIES_TEXT]

        return entities
