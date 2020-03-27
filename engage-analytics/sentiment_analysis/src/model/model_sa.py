import sentiment_analysis.src.constants as cons
import warnings, os
import sentiment_analysis.src.constants as global_cons

warnings.filterwarnings("ignore")

from sentiment_analysis.src.model.model_emoji import ModelEmoji
from sentiment_analysis.src.model.frequency_words import FrequencyWords
from sentiment_analysis.src.model.build_hist import BuildHistogram
from sentiment_analysis.src.model.positiveness_negativeness import PositivenessNegativeness
from sentiment_analysis.src.clean_comments import CleanComments
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from utils.gcloud.nlp_client import NLPGoogleClient
from sentiment_analysis.src.model.labelling_interface import InterfaceLabel
from utils.data_connection.redis_manager import RedisManager


class ModelsSentimentAnalysis:

    def __init__(self, redis: RedisManager, company_id: str):
        self.__redis = redis
        self.__company_id = company_id
        self.__model = self.__load_model(company_id=self.__company_id)
        self.__model_tf = self.__model.get(self.__company_id).get("TF_W")
        self.__diff_pos = self.__model.get(self.__company_id).get("diff_pos")
        self.__diff_neg = self.__model.get(self.__company_id).get("diff_neg")
        self.__google_client = NLPGoogleClient.open_client()

        self.__threshold_neg, self.__threshold_pos = InterfaceLabel.calculate_threshold_positive_negative(
            self.__fetch_company_historical_data())

    @property
    def model(self):
        return self.__model

    def __load_model(self, company_id: str) -> dict:
        """
        retrieve model from redis
        :param company_id: string of company_id
        :return:
        """
        model = self.__redis.retrieve(key=company_id, field="")
        if not model:
            model = {company_id: {"TF_W": {},
                                  "diff_pos": [],
                                  "diff_neg": []}}
        return model

    @staticmethod
    def __clean_text(text) -> str:
        """
        Clean the text
        :param text: text to analyze
        :return:
        """
        splitted_word = CleanComments.decode_html_entities(text)
        splitted_word = CleanComments.filter_special_characters(splitted_word)
        splitted_word = splitted_word.lower()
        splitted_word = CleanComments.filter_stopwords(cons.lang_english, splitted_word)
        return splitted_word

    def __cleaning_split(self, text: str) -> list:
        """
        Run the cleansing and splitting commands
        :param text: text to analyze
        :return:
        """
        splitted_word = self.__clean_text(text)
        splitted_word = splitted_word.split()
        return splitted_word

    def emoji_model(self,
                    text: str,
                    sentiment: str) -> str:
        """
        Evaluate the text if has emojis and changes sentiments
        :param text: text to analyse
        :param sentiment: sentiment of given text
        :return:
        """
        emoji = ModelEmoji(text=text, sentiment=sentiment)
        return emoji.detect_emoji_sentiment()

    def __build_histogram(self,
                          sentiment: str,
                          freq_words: FrequencyWords,
                          splitted_word: list,
                          calibrate: bool = False) -> tuple:
        """
        Build the histogram and calculate the mean
        :param sentiment: sentiment to be assessed in Histogram
        :param freq_words: inject class to calibrate model
        :param splitted_word: list wth the words of the text
        :param calibrate: bool indicating to calibrate or not the histogram
        :return:
        """
        model_dict_norm = freq_words.norm_dict_freq(freq_dict=self.__model)
        build = BuildHistogram(sentiment_text=sentiment,
                               splitted_word=splitted_word,
                               freq_norm=model_dict_norm,
                               difference_pos=self.__diff_pos,
                               difference_neg=self.__diff_neg,
                               calibrate=calibrate
                               )
        build.run_histogram()

        return build.mean_pos, build.mean_neg, build.difference_pos, build.difference_neg, model_dict_norm

    @staticmethod
    def __frequency_model(freq_words: FrequencyWords,
                          calibrate_neutral: bool = False) -> dict:

        """
        Build the frequency model
        :param freq_words: inject class to calibrate model
        :param calibrate_neutral: bool to calibrate frequency model or not
        :return:
        """

        if calibrate_neutral:
            freq_words.calibrate_frequency(calibrate_neutral=calibrate_neutral)

        return freq_words.freq

    @staticmethod
    def __change_sentiment(mean_pos: float,
                           mean_neg: float,
                           splitted_word: list,
                           model_dict_norm: dict,
                           sentiment: str) -> str:
        """
        Change the sentiment of the text if is needed
        :param mean_pos: mean positive of the histogram
        :param mean_neg: mean negative of the histogram
        :param splitted_word: list wth the words of the text
        :param model_dict_norm: normalized dict data from model
        :param sentiment: initial sentiment to be assessed
        :return:
        """

        diff_poss_neg = PositivenessNegativeness.calculate_difference(splitted_word=splitted_word,
                                                                      freq_norm=model_dict_norm)

        if sentiment.lower() == global_cons.NEUTRAL and (diff_poss_neg > mean_pos):
            sentiment = global_cons.POSITIVE
        elif sentiment.lower() == global_cons.NEUTRAL and (diff_poss_neg < mean_neg):
            sentiment = global_cons.NEGATIVE

        return sentiment

    def __calculate_gcloud_score(self, text) -> float:
        """
        Calculate score from external tool: Google Cloud
        :param text: text to be analysed
        :return: score
        """
        __, sentiment_score = ClientsLanguageSentiment.dominant_language_sentiment_text(self.__google_client, text)

        return sentiment_score

    def predict_on_emoji(self, data_sent_text: dict) -> str:
        """
        Predict the text using emoji
        :param data_sent_text: dictionary with the text and sentiment
        :return: sentiment considering emojis
        """
        sentiment = self.emoji_model(text=data_sent_text.get("text"),
                                     sentiment=data_sent_text.get("sentiment"))

        return sentiment

    def __fetch_company_historical_data(self) -> list:
        """
        Fetches data from redis regarding a specific company
        :return:
        """
        processing_result = {}
        try:
            survey_data = self.__redis.retrieve(key=self.__company_id, field="score")

            # If data for given period exists
            if survey_data:
                processing_result = survey_data
        except Exception:
            return {}

        if not processing_result:
            raise Exception("No baseline data found on Redis.")

        return processing_result

    def __classify_using_historical_data(self, text: str) -> tuple:
        """
        Process surveys score from information on redis, as a historical method
        :param text: raw text to detect sentiment
        :return: score and sentiment
        """
        score = self.__calculate_gcloud_score(text=text)
        sentiment = ""

        if self.__threshold_pos is not None and self.__threshold_neg is not None:
            sentiment = InterfaceLabel.label_sentiment(score=score,
                                                       thresholds=(self.__threshold_neg, self.__threshold_pos))

        return score, sentiment

    def train(self, data_sent_text: dict) -> tuple:
        """
        Train the model and return the dictionary of the model
        :param data_sent_text: dictionary with the text and sentiment
        :return:
        """
        text = data_sent_text.get("text")
        sentiment = data_sent_text.get("sentiment")
        splitted_word = self.__cleaning_split(text)
        freq_words = FrequencyWords(sentiment=sentiment,
                                    freq=self.__model,
                                    splitted_word=splitted_word)

        self.__model = self.__frequency_model(freq_words=freq_words,
                                              calibrate_neutral=True)
        __, __, diff_pos, diff_neg, __ = self.__build_histogram(sentiment=sentiment,
                                                                freq_words=freq_words,
                                                                splitted_word=splitted_word,
                                                                calibrate=True)

        return self.__model, diff_pos, diff_neg

    def predict(self, text: str) -> dict:
        """
        Predict sentiment analysis based on raw text
        :param text: raw text to predict
        :return:
        """

        splitted_word = self.__cleaning_split(text)

        # Historical data sentiment
        score, sentiment = self.__classify_using_historical_data(text=text)

        # Neutralness sentiment evaluation
        # TODO: Activate this when we have enough TF in redis
        if False:
            freq_words = FrequencyWords(sentiment=sentiment,
                                        freq=self.__model,
                                        splitted_word=splitted_word)
            mean_pos, mean_neg, __, __, model_dict_norm = self.__build_histogram(sentiment=sentiment,
                                                                                 freq_words=freq_words,
                                                                                 splitted_word=splitted_word,
                                                                                 calibrate=False)

            sentiment = self.__change_sentiment(mean_pos=mean_pos,
                                                mean_neg=mean_neg,
                                                splitted_word=splitted_word,
                                                model_dict_norm=model_dict_norm,
                                                sentiment=sentiment)

        # Emoji sentiment
        sentiment = self.emoji_model(text=text, sentiment=sentiment)

        return {"text": text, "sentiment": sentiment, "score": score}
