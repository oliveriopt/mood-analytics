import emoji
import sentiment_analysis.src.report.cons_report as cons
import sentiment_analysis.src.constants as global_cons

from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.utilities import read_json_file, CUSTOM_YEAR_WEEK_AGG, extract_dimension, extract_question
from sentiment_analysis.src.word_cloud import words_clouds
from sentiment_analysis.src.clients_language_sentiments_entity import ClientsLanguageSentiment
from nested_lookup import nested_lookup


class InterFaceReport:

    def __init__(self, topics: dict, surveys: dict, company_id: str, weeks: list,
                 g_client: ClientsLanguageSentiment,
                 api_source_manager: APISourcesFetcher):

        self.topics = topics
        self.surveys = surveys
        self.company_id = company_id
        self.weeks = weeks
        self.g_client = g_client
        self.api_source_manager = api_source_manager

        self.thresholds = ()
        self.table_surveys_replies = []
        self.table_topics = []
        self.table_topic_comment = []
        self.counter_text_sr = None
        self.counter_text_topics = None
        self.info_file = read_json_file("en_US.json")
        self.image_base64_sr = None
        self.image_base64_topics = None

    def sort_by_dimension_sentiment_table(self) -> None:
        """
        Sort by dimension and by sentiment
        :return:
        """

        temp_table = []
        for dimension in cons.dimensions:
            temp = [d for d in self.table_surveys_replies if d['dimension'] == dimension]
            temp = sorted(temp, key=lambda k: k['sentiment'], reverse=True)
            temp_table.extend(temp)
        self.table_surveys_replies = temp_table

    def insert_to_list_surveys_replies(self, features: list, company_week: int) -> None:
        """
        Create array with the dictionary for interface
        :param features: list of features to extract
        :param company_week: company week of the company
        :return:
        """

        for item_analyze in features:
            question = extract_question(self.info_file, dimension=item_analyze[0], week=company_week)
            dimension = extract_dimension(self.info_file, dimension=item_analyze[0])
            comment = item_analyze[1]
            sentiment = item_analyze[2]

            temp = {}
            temp.update(dimension=dimension)
            temp.update(question=question)
            temp.update(comment=emoji.emojize(comment, use_aliases=True))
            temp.update(sentiment=sentiment)
            self.table_surveys_replies.append(temp)

        self.sort_by_dimension_sentiment_table()

    def insert_to_list_topics(self, features: list) -> None:
        """
        Create array with the dictionary for interface - referenced to topic headlines
        :param features: list of features to extract
        :return:
        """

        for item_analyze in features:
            topic_id = item_analyze[0]
            comment = item_analyze[1]
            sentiment = item_analyze[2]

            temp = {}
            temp.update(id=topic_id)
            temp.update(comment=emoji.emojize(comment, use_aliases=True))
            temp.update(sentiment=sentiment)
            self.table_topics.append(temp)

        self.table_topics = sorted(self.table_topics, key=lambda k: k['sentiment'], reverse=True)

    def insert_to_list_topic_comments(self, features: list) -> None:
        """
        Create array with the dictionary for interface - referenced to topic comments
        :param features: list of features to extract
        :return:
        """

        for item_analyze in features:
            topic_id_comment_id = item_analyze[0]
            comment = item_analyze[1]
            sentiment = item_analyze[2]

            temp = {}
            temp.update(id=topic_id_comment_id)
            temp.update(comment=emoji.emojize(comment, use_aliases=True))
            temp.update(sentiment=sentiment)
            self.table_topic_comment.append(temp)

        self.table_topic_comment = sorted(self.table_topic_comment, key=lambda k: k['sentiment'], reverse=True)

    def word_cloud(self):
        """
        Create wordcloud of the main words
        :return:
        """

        self.image_base64_sr = words_clouds(self.counter_text_sr, cons.path_image_sr_wc)
        self.image_base64_topics = words_clouds(self.counter_text_topics, cons.path_image_topics_wc)

    @staticmethod
    def __count_filter_keys(entities: list) -> object:
        """
        Count and filter keys
        :param entities: list of entities text
        :return:
        """
        entities = ClientsLanguageSentiment.count_entities(entities=entities)
        entities = ClientsLanguageSentiment.filter_black_list(entities=entities)

        return entities

    def __process_sr(self) -> None:
        """
        Process the surveys replies
        :return:
        """
        for company_id, periods in self.surveys.items():
            for period in self.weeks:
                period_parts = period.split(CUSTOM_YEAR_WEEK_AGG)
                translations_week = self.api_source_manager.get_company_week_from_period(week=period_parts[0],
                                                                                         year=period_parts[1],
                                                                                         company_id=self.company_id)

                sr_dimension = nested_lookup(global_cons.SR_DIMENSION, periods)
                sr_content = nested_lookup(global_cons.SR_CONTENT, periods)
                sr_sentiment = nested_lookup(global_cons.SENTIMENT, periods)
                sr_entities = nested_lookup(global_cons.SR_ENTITIES, periods)

                sr_comment_score = list(zip(sr_dimension, sr_content, sr_sentiment))

                self.insert_to_list_surveys_replies(sr_comment_score, company_week=translations_week)
                self.counter_text_sr = self.__count_filter_keys(entities=sr_entities)

    def __process_topics(self) -> None:
        """
        Process the topics
        :return:
        """
        for company_id, topics in self.topics.items():
            # heading
            topic_headings = nested_lookup(global_cons.TOPIC_CONTENT, topics)
            topic_headings_sentiments = nested_lookup(global_cons.TOPIC_SENTIMENT, topics)
            topic_ids = list(topics.keys())
            topic_w_sentiments = list(zip(topic_ids, topic_headings, topic_headings_sentiments))
            self.insert_to_list_topics(topic_w_sentiments)

            # comments
            for topic_id, topic in topics.items():
                topic_comments = nested_lookup(global_cons.TOPIC_COMMENT, topic)
                topic_comments_scores = nested_lookup(global_cons.TOPIC_COMMENT_SENTIMENT, topic)
                topic_list_ids = [topic_id] * len(topic_comments)
                topic_w_scores = list(zip(topic_list_ids, topic_comments, topic_comments_scores))
                self.insert_to_list_topic_comments(topic_w_scores)

            entities = nested_lookup(global_cons.TOPIC_ENTITIES, topics)
            self.counter_text_topics = ClientsLanguageSentiment.count_entities(entities)

    def process_interface(self) -> None:
        """
        Take the info needed to write into report_pdf
        :return:
        """
        self.__process_sr()
        self.__process_topics()
