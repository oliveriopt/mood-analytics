from utils.utilities import get_start_and_end_date_from_calendar_week


class HtmlDocument:

    def __init__(self):
        self.html_doc = """"""

    def open_html_document(self) -> str:
        """
        Open HTML document
        :return:
        """
        self.html_doc = self.html_doc + ("""<!DOCTYPE report_html>
            <report_html>\n""")
        return self.html_doc

    def write_title(self, title: str, cw: int, year: int, class_txt: str) -> str:
        """
        Write title on HTML document
        :param title:
        :param cw:
        :param year:
        :param class_txt:
        :return:
        """
        str_title = """<h1 class=\"""" + class_txt + """ text-center\">""" + title + """</h1>""" \
                    + """<h3 class = \"text-center\">""" + """Week """ + str(cw) + """: """ + str(
            get_start_and_end_date_from_calendar_week(year, cw)[0]) + """ to """ + str(
            get_start_and_end_date_from_calendar_week(year, cw)[1] \
            + """</h3>""")
        self.html_doc = self.html_doc + str_title
        return self.html_doc

    def write_subtitle(self, subtitle: str, break_page: bool, class_txt: str) -> str:
        """
        Write subtitle on HTML document
        :param subtitle:
        :param break_page:
        :param class_txt:
        :return:
        """
        if break_page:
            str_title = """<h2 class="break-before">""" + subtitle + """</h2>\n"""
        else:
            str_title = """<h2 class=\"""" + class_txt + """\">""" + subtitle + """</h2>\n"""
        self.html_doc = self.html_doc + str_title
        return self.html_doc

    def open_head(self) -> str:
        """
        Open head on HTML document
        :return:
        """
        self.html_doc = self.html_doc + """<head>"""
        return self.html_doc

    def close_head(self) -> str:
        """
        Close head on HTML document
        :return:
        """
        self.html_doc = self.html_doc + """</head>"""
        return self.html_doc

    def meta(self) -> str:
        """
        Write meta on report_html document
        :return:
        """
        meta = """<meta charset="utf-8" >\n <meta name="viewport" content="width=device-width, initial-scale=1" >\n"""
        self.html_doc = self.html_doc + meta
        return self.html_doc

    def link_bootstrap(self) -> str:
        """
        Write link bootstrap on report_html document
        :return:
        """
        link = """<link
        href = "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
        rel = "stylesheet" >\n"""
        self.html_doc = self.html_doc + link
        return self.html_doc

    def open_style(self) -> str:
        """
        Open style on report_html document
        :return:
        """
        self.html_doc = self.html_doc + """<style>\n"""
        return self.html_doc

    def style_title(self) -> str:
        """
        Write style title on report_html document
        :return:
        """
        style_title = """.title
    {margin-bottom: 10px}\n"""
        self.html_doc = self.html_doc + style_title
        return self.html_doc

    def style_spacer_xs(self) -> str:
        """
        Write style spacer xs on report_html document
        :return:
        """
        style_spacer_xs = """.spacer--xs
    {margin-bottom: 15px;}\n"""
        self.html_doc = self.html_doc + style_spacer_xs
        return self.html_doc

    def style_spacer_md(self) -> str:
        """
        Write style spacer md on report_html document
        :return:
        """
        style_spacer_md = """.spacer--md
    {margin-top: 55px;
    margin-bottom: 25px;}\n"""
        self.html_doc = self.html_doc + style_spacer_md
        return self.html_doc

    def style_spacer_lg(self) -> str:
        """
        Write style spacer lg on report_html document
        :return:
        """
        style_spacer_lg = """.spacer--lg
    {margin-top: 55px;
    margin-bottom: 55px;}\n"""
        self.html_doc = self.html_doc + style_spacer_lg
        return self.html_doc

    def style_page_break(self) -> str:
        """
        Write style page break md on report_html document
        :return:
        """
        page_break = """.break-before
        {margin-top: 55px;\n
        margin-bottom: 55px;\n
        page-break-before: always;}\n"""
        self.html_doc = self.html_doc + page_break
        return self.html_doc

    def style_resize(self) -> str:
        """
        Write style resize on report_html document
        :return:
        """
        resize = """.resize{
        width: 1000px;
        height: auto;}\n"""
        self.html_doc = self.html_doc + resize
        return self.html_doc

    def class_font_size(self, size) -> str:

        size_str = """.table--size-md{
        font-size: """ + str(size) + """px}"""
        self.html_doc = self.html_doc + size_str
        return self.html_doc

    def close_style(self) -> str:
        """
        Close style on report_html document
        :return:
        """
        self.html_doc = self.html_doc + """</style>\n"""
        return self.html_doc

    def insert_image(self, image64: str, class_txt: str, height: int, width: int) -> str:
        """
        Insert image on report_html document
        :param image64: string base 64 of image
        :param class_txt: string of the class text
        :param height: height of the image
        :param width: width of the image
        :return:
        """
        if (height is None) & (width is None):
            image = """<div class="text-center">
        <img class="resize" src="data:image/png;base64, """ + image64 + """"/>\n
    </div>"""
        else:
            image = """<div>
                <img class=""" + class_txt + """ src="data:image/png;base64, """ + image64 + """"" height=""" + str(
                height) + """ width=""" + str(
                width) + """/>\n
            </div>
            """

        self.html_doc = self.html_doc + image
        return self.html_doc

    def open_body(self) -> str:
        """
        Open body of the report_html document
        :return:
        """
        self.html_doc = self.html_doc + """<body>\n
    """
        return self.html_doc

    def close_body(self) -> str:
        """
        Close body of the report_html document
        :return:
        """
        self.html_doc = self.html_doc + """</body>\n
    """
        return self.html_doc

    def close(self) -> str:
        """
        Close of the report_html document
        :return:
        """
        self.html_doc = self.html_doc + """</report_html>\n
    """
        return self.html_doc


class HtmlTable:
    def __init__(self) -> str:
        self.html_table = """ """

    def open(self) -> str:
        """
        Open table on report_html document
        :return:
        """
        self.html_table = self.html_table + """<table class ="table table-striped">\n"""
        return self.html_table

    def close(self) -> str:
        """
        Close table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</table>\n"""
        return self.html_table

    def open_thead(self) -> str:
        """
        Open head of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """<thead>\n"""
        return self.html_table

    def close_thead(self) -> str:
        """
        Close head of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</thead>\n"""
        return self.html_table

    def open_cell_head(self, width) -> str:
        """
        Open cell head of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """<th width=""" + str(width) + """>"""
        return self.html_table

    def close_cell_head(self) -> str:
        """
        Close cell head of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</th>\n"""
        return self.html_table

    def open_row(self) -> str:
        """
        Open row of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """<tr>\n"""
        return self.html_table

    def close_row(self) -> str:
        """
        Close row of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</tr>\n"""
        return self.html_table

    def open_cell(self, color: str) -> str:
        """
        Open cell of the table on report_html document
        :return:
        """
        if color is None:
            self.html_table = self.html_table + """<td>"""
        else:
            self.html_table = self.html_table + """<td style = "color:""" + color + """">"""
        return self.html_table

    def close_cell(self) -> str:
        """
        Close cell of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</td>\n"""
        return self.html_table

    def open_body(self) -> str:
        """
        Open body of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """<tbody class="table--size-md">\n"""
        return self.html_table

    def close_body(self) -> str:
        """
        Close body of the table on report_html document
        :return:
        """
        self.html_table = self.html_table + """</tbody> \n"""
        return self.html_table
