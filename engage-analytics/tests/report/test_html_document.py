from unittest import TestCase

from sentiment_analysis.src.report_html.utilities_html import HtmlDocument
from utils.utilities import get_start_and_end_date_from_calendar_week


class TestHTMLReport(TestCase):

    def setUp(self):
        self.document = HtmlDocument()

    def test_open_html_document(self):
        html_doc = self.document.open_html_document()

        assert html_doc == """<!DOCTYPE report_html>
            <report_html>\n"""

    def test_write_title(self):
        self.document.open_html_document()
        year = 2019
        cw = 10
        class_txt = "spacer--md"

        init_date, end_date = get_start_and_end_date_from_calendar_week(year, cw)
        title = self.document.write_title(title="xpto",
                                          cw=cw,
                                          year=2019,
                                          class_txt=class_txt)

        expected = f"""<!DOCTYPE report_html>
            <report_html>
<h1 class="{class_txt} text-center">xpto</h1><h3 class = "text-center">Week {cw}: {init_date} to {end_date}</h3>"""

        assert title == expected

    def test_write_subtitle_no_break(self):
        self.document.open_html_document()

        class_txt = "spacer--md"
        subtitle = "xpto"
        title = self.document.write_subtitle(subtitle=subtitle,
                                             break_page=False,
                                             class_txt=class_txt)

        expected = f"""<!DOCTYPE report_html>
            <report_html>
<h2 class="{class_txt}">{subtitle}</h2>\n"""

        assert title == expected

    def test_write_subtitle_with_break(self):
        self.document.open_html_document()

        class_txt = "spacer--md"
        subtitle = "xpto"
        title = self.document.write_subtitle(subtitle=subtitle,
                                             break_page=True,
                                             class_txt=class_txt)

        expected = f"""<!DOCTYPE report_html>
            <report_html>
<h2 class="break-before">{subtitle}</h2>\n"""

        assert title == expected

    def test_open_head(self):
        self.document.open_html_document()

        head = self.document.open_head()

        expected = """<!DOCTYPE report_html>
            <report_html>
<head>"""

        assert head == expected

    def test_meta(self):
        self.document.open_html_document()

        meta = self.document.meta()

        expected = """<!DOCTYPE report_html>
            <report_html>
<meta charset="utf-8" >\n <meta name="viewport" content="width=device-width, initial-scale=1" >\n"""

        assert meta == expected

    def test_link_bootstrap(self):
        self.document.open_html_document()

        bootstrap_link = self.document.link_bootstrap()

        expected = """<!DOCTYPE report_html>
            <report_html>
<link
        href = "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
        rel = "stylesheet" >\n"""

        assert bootstrap_link == expected

    def test_open_style(self):
        self.document.open_html_document()

        style = self.document.open_style()

        expected = """<!DOCTYPE report_html>
            <report_html>
<style>\n"""

        assert style == expected

    def test_style_title(self):
        self.document.open_html_document()

        style = self.document.style_title()

        expected = """<!DOCTYPE report_html>
            <report_html>
.title
    {margin-bottom: 10px}\n"""

        assert style == expected

    def test_style_spacer_xs(self):
        self.document.open_html_document()

        style = self.document.style_spacer_xs()

        expected = """<!DOCTYPE report_html>
            <report_html>
.spacer--xs
    {margin-bottom: 15px;}\n"""

        assert style == expected

    def test_style_spacer_md(self):
        self.document.open_html_document()

        style = self.document.style_spacer_md()

        expected = """<!DOCTYPE report_html>
            <report_html>
.spacer--md
    {margin-top: 55px;
    margin-bottom: 25px;}\n"""

        assert style == expected

    def test_style_spacer_lg(self):
        self.document.open_html_document()

        style = self.document.style_spacer_lg()

        expected = """<!DOCTYPE report_html>
            <report_html>
.spacer--lg
    {margin-top: 55px;
    margin-bottom: 55px;}\n"""

        assert style == expected

    def test_style_page_break(self):
        self.document.open_html_document()

        style = self.document.style_page_break()

        expected = """<!DOCTYPE report_html>
            <report_html>
.break-before
        {margin-top: 55px;\n
        margin-bottom: 55px;\n
        page-break-before: always;}\n"""

        assert style == expected

    def test_style_resize(self):
        self.document.open_html_document()

        style = self.document.style_resize()

        expected = """<!DOCTYPE report_html>
            <report_html>
.resize{
        width: 1000px;
        height: auto;}\n"""

        assert style == expected

    def test_class_font_size(self):
        self.document.open_html_document()

        font_size = self.document.class_font_size(size=10)

        expected = """<!DOCTYPE report_html>
            <report_html>
.table--size-md{
        font-size: 10px}"""

        assert font_size == expected

    def test_close_style(self):
        self.document.open_html_document()

        style = self.document.close_style()

        expected = """<!DOCTYPE report_html>
            <report_html>
</style>\n"""

        assert style == expected

    def test_insert_image_with_sizes(self):
        self.document.open_html_document()

        image = self.document.insert_image(image64="xpto", class_txt="xpto", height=100, width=100)

        expected = """<!DOCTYPE report_html>
            <report_html>
<div>
                <img class=xpto src="data:image/png;base64, xpto"" height=100 width=100/>

            </div>
            """

        assert image == expected

    def test_insert_image_without_sizes(self):
        self.document.open_html_document()

        image = self.document.insert_image(image64="xpto", class_txt="xpto", height=None, width=None)

        expected = """<!DOCTYPE report_html>
            <report_html>
<div class="text-center">
        <img class="resize" src="data:image/png;base64, xpto"/>

    </div>"""

        assert image == expected

    def test_open_body(self):
        self.document.open_html_document()

        body = self.document.open_body()

        expected = """<!DOCTYPE report_html>
            <report_html>
<body>

    """

        assert body == expected

    def test_close_body(self):
        self.document.open_html_document()

        body = self.document.close_body()

        expected = """<!DOCTYPE report_html>
            <report_html>
</body>

    """

        assert body == expected

    def test_close(self):
        self.document.open_html_document()

        body = self.document.close()

        expected = """<!DOCTYPE report_html>
            <report_html>
</report_html>

    """
        assert body == expected
