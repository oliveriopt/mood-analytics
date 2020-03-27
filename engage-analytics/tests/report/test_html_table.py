from unittest import TestCase

from sentiment_analysis.src.report_html.utilities_html import HtmlTable


class TestHTMLTable(TestCase):

    def setUp(self):
        self.table = HtmlTable()

    def test_open_html_table(self):
        html_doc = self.table.open()
        expected = """ <table class ="table table-striped">\n"""

        assert html_doc == expected

    def test_close_html_table(self):
        html_doc = self.table.close()

        expected = """ </table>\n"""

        assert html_doc == expected

    def test_open_thead(self):
        html_doc = self.table.open_thead()

        expected = """ <thead>\n"""

        assert html_doc == expected

    def test_close_thead(self):
        html_doc = self.table.close_thead()

        expected = """ </thead>\n"""

        assert html_doc == expected

    def test_open_cell_head(self):
        html_doc = self.table.open_cell_head(width=10)

        expected = """ <th width=10>"""

        assert html_doc == expected


    def test_close_cell_head(self):
        html_doc = self.table.close_cell_head()

        expected = """ </th>\n"""

        assert html_doc == expected


    def test_open_row(self):
        html_doc = self.table.open_row()

        expected = """ <tr>\n"""

        assert html_doc == expected


    def test_close_row(self):
        html_doc = self.table.close_row()

        expected = """ </tr>\n"""

        assert html_doc == expected


    def test_open_cell_no_color(self):
        html_doc = self.table.open_cell(color=None)

        expected = """ <td>"""

        assert html_doc == expected

    def test_open_cell_w_color(self):
        html_doc = self.table.open_cell(color="xpto")
        expected = """ <td style = "color:xpto">"""

        assert html_doc == expected

    def test_close_cell(self):
        html_doc = self.table.close_cell()
        expected = """ </td>\n"""

        assert html_doc == expected

    def test_open_body(self):
        html_doc = self.table.open_body()
        expected = """ <tbody class="table--size-md">\n"""

        assert html_doc == expected

    def test_close_body(self):
        html_doc = self.table.close_body()
        expected = """ </tbody> \n"""

        assert html_doc == expected