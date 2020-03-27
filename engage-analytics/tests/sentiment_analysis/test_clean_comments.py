import unittest

from sentiment_analysis.src.clean_comments import CleanComments


class TestCleanComments(unittest.TestCase):

    def setUp(self):
        self.text = "w&auml;re SCH&ouml;n mö&ouml;glic &uuml; # $ ?*+ john-doe D'Vito"
        self.stopwords_en_text = "this is a sample sentence showing off the stop words filtration no"
        self.stopwords_de_text = "aber ware schön möglic ü mit keine"

    def tearDown(self):
        del self.text, self.stopwords_en_text, self.stopwords_de_text

    def test_decode_html_entities(self):
        decoded_text = CleanComments.decode_html_entities(self.text)

        assert isinstance(decoded_text, str)
        assert decoded_text == "wäre SCHön mööglic ü # $ ?*+ john-doe D'Vito"

    def test_filter_special_characters_lower(self):
        filtered_text = CleanComments.filter_special_characters(self.text)

        assert isinstance(filtered_text, str)
        assert filtered_text == "w auml re SCH ouml n mö ouml glic  uuml          john-doe D'Vito"

    def test_filter_new_line_carriage_return(self):
        filtered_text = CleanComments.filter_special_characters(self.text + "\n\n")

        assert isinstance(filtered_text, str)
        assert filtered_text == "w auml re SCH ouml n mö ouml glic  uuml          john-doe D'Vito  "

    def test_filter_dashed_words(self):
        filtered_text = CleanComments.filter_special_characters(self.text + "\n\n")

        assert isinstance(filtered_text, str)
        assert filtered_text == "w auml re SCH ouml n mö ouml glic  uuml          john-doe D'Vito  "

    def test_filter_stopwords(self):
        filtered_stopwords_en = CleanComments.filter_stopwords("en", self.stopwords_en_text)
        assert isinstance(filtered_stopwords_en, str)
        assert filtered_stopwords_en == "sample sentence showing stop words filtration no"

        filtered_stopwords_de = CleanComments.filter_stopwords("de", self.stopwords_de_text)
        assert isinstance(filtered_stopwords_de, str)
        assert filtered_stopwords_de == "ware schön möglic ü keine"

    def test_filter_urls(self):
        text = "https://www.focus.de/politik/deutschland/fakt-fake-kolumne-von-josef-seitz-.html Beim Lesen des Artikel ist mir persö nlich übel geworden"

        filtered_urls = CleanComments.filter_urls(comment=text)
        assert isinstance(filtered_urls, str)
        assert filtered_urls == " beim lesen des artikel ist mir persö nlich übel geworden"

    def test_strip_emojis(self):
        text = "Anika 🙌"

        filtered_emojis = CleanComments.strip_emojis(comment=text)
        assert isinstance(filtered_emojis, str)
        assert filtered_emojis == "Anika "

    def test_strip_emoticons(self):
        text = "Anika :-) :D"

        filtered_emoticons = CleanComments.strip_emojis(comment=text)
        assert isinstance(filtered_emoticons, str)
        assert filtered_emoticons == "Anika  "

    def test_filter_words_without_numbers(self):
        text = "abc 123 co2 1.4 2,5"

        filtered = CleanComments.filter_words_without_numbers(comment=text)
        assert isinstance(filtered, str)
        assert filtered == "abc  co  "

    def test_filter_spaces(self):
        text = "abc \n   abc"

        filtered = CleanComments.filter_spaces(comment=text)
        assert isinstance(filtered, str)
        assert filtered == "abc abc"

    def test_filter_special_chars_surrounded_spaces(self):
        text = "abc - abc"

        filtered = CleanComments.filter_special_chars_surrounded_spaces(comment=text)
        assert isinstance(filtered, str)
        assert filtered == "abc abc"
