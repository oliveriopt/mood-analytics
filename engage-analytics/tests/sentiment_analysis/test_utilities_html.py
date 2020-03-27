from unittest import TestCase, mock
from sentiment_analysis.src.report_html.utilities_html import HtmlDocument, HtmlTable


class TestHtmlDocument(TestCase):

    def setUp(self):
        self.html_doc = HtmlDocument()
        self.start_end_date = ("Monday, September 02 2019", "Friday, September 06 2019")

    def tearDown(self):
        del self.html_doc

    def test_open_html_document(self):
        string = self.html_doc.open_html_document()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<!DOCTYPE report_html><report_html>\n")

    @mock.patch('utils.utilities.get_start_and_end_date_from_calendar_week', autospec=True)
    def test_write_title(self, start_end_date):
        cw = 35
        year = 2019
        title = "Report for Sentiment Analysis"
        class_txt = "spacer--md"
        string = self.html_doc.write_title(title, cw, year, class_txt)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<h1 class=\"spacer--md text-center\">"
                                "Report for Sentiment Analysis</h1><h2 class = \"text-center\">"
                                "Week 35: Monday, August 26 2019 to Friday, August 30 2019</h2>")

    def test_write_subtitle_break_page_true(self):
        subtitle = "Surveys Replies by type of sentiment"
        break_page = True
        class_txt = "spacer--md"
        string = self.html_doc.write_subtitle(subtitle, break_page, class_txt)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<h2 class=\"break-before\">Surveys Replies by type of sentiment</h2>")

    def test_write_subtitle_break_page_false(self):
        subtitle = "Surveys Replies by type of sentiment"
        break_page = False
        class_txt = "spacer--md"
        string = self.html_doc.write_subtitle(subtitle, break_page, class_txt)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<h2 class=\"spacer--md\">Surveys Replies by type of sentiment</h2>")

    def test_open_head(self):
        string = self.html_doc.open_head()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<head>")

    def test_close_head(self):
        string = self.html_doc.close_head()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</head>")

    def test_meta(self):
        string = self.html_doc.meta()
        self.assertIsInstance(string, str)
        self.assertTrue(string,
                        "<meta charset=\"utf-8\" >\n <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" >\n")

    def test_link_bootstrap(self):
        string = self.html_doc.link_bootstrap()
        self.assertIsInstance(string, str)
        self.assertTrue(string,
                        "<link href = \"https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css\" rel = \"stylesheet\" >\n")

    def test_open_style(self):
        string = self.html_doc.open_style()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<style>\n")

    def test_style_title(self):
        string = self.html_doc.style_title()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".title {margin-bottom: 10px}\n")

    def test_style_spacer_xs(self):
        string = self.html_doc.style_spacer_xs()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".spacer--xs {margin-bottom: 15px;}\n")

    def test_style_spacer_md(self):
        string = self.html_doc.style_spacer_md()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".spacer--md {margin-top: 55px; margin-bottom: 25px;}\n")

    def test_style_spacer_lg(self):
        string = self.html_doc.style_spacer_lg()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".spacer--lg {margin-top: 55px; margin-bottom: 55px;}\n")

    def test_style_page_break(self):
        string = self.html_doc.style_page_break()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".break-before {margin-top: 55px;\n"
                                "margin-bottom: 55px;\n"
                                "page-break-before: always;}\n")

    def test_style_resize(self):
        string = self.html_doc.style_resize()
        self.assertIsInstance(string, str)
        self.assertTrue(string, ".resize{ width: 1000px; height: auto;}\n")

    def test_close_style(self):
        string = self.html_doc.close_style()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</style>\n")

    def test_open_body(self):
        string = self.html_doc.open_body()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<body>\n")

    def test_close_body(self):
        string = self.html_doc.close_body()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</body>\n")

    def test_close(self):
        string = self.html_doc.close()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</report_html>\n")

    def test_write_subtitle_insert_image_none(self):
        path_image = "/usr/etc/image/kununu.png"
        height = None
        width = None
        class_txt = "spacer--md"
        string = self.html_doc.insert_image(path_image, class_txt, height, width)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<div class=\"text-center\"> <img class=\"resize\" src=/usr/etc/image/kununu.png/>")

    def test_write_subtitle_insert_image_size(self):
        path_image = "/usr/etc/image/kununu.png"
        height = 1000
        width = 1000
        class_txt = "spacer--md"
        string = self.html_doc.insert_image(path_image, class_txt, height, width)
        self.assertIsInstance(string, str)
        self.assertTrue(string,
                        "<div> <img class=spacer--md src=/usr/etc/image/kununu.png height=1000 width=1000/> </div>")


class TestHtmlTable(TestCase):

    def setUp(self):
        self.table = HtmlTable()
        self.color = "red"
        self.color_none = None
        self.width = 100

    def tearDown(self):
        del self.table

    def test_open(self):
        string = self.table.open()
        self.assertIsInstance(string, str)
        self.assertTrue(string, " <table class =\"table table-striped\">")

    def test_close(self):
        string = self.table.close()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</table>\n")

    def test_open_thead(self):
        string = self.table.open_thead()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<thead>\n")

    def test_close_thead(self):
        string = self.table.close_thead()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</thead>\n")

    def test_open_cell_head(self):
        string = self.table.open_cell_head(str(self.width))
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<th width=100>")

    def test_close_cell_head(self):
        string = self.table.close_cell_head()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</th>\n")

    def test_open_row(self):
        string = self.table.open_row()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<tr>\n")

    def test_close_row(self):
        string = self.table.close_row()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</tr>\n")

    def test_open_cell(self):
        string = self.table.open_cell(self.color)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<td style = \"color:red\">")

    def test_open_cell_color_none(self):
        string = self.table.open_cell(self.color_none)
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<td>")

    def test_close_cell(self):
        string = self.table.close_cell()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</td>\n")

    def test_open_body(self):
        string = self.table.open_body()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "<tbody>\n")

    def test_close_body(self):
        string = self.table.close_cell_head()
        self.assertIsInstance(string, str)
        self.assertTrue(string, "</tbody> \n")
