import sentiment_analysis.src.report.cons_report as cons
import logging
import sys

from utils.utilities import define_color, convert_path_image_64, get_project_path
from sentiment_analysis.src.report_html.utilities_html import *

logger = logging.getLogger()


def write_style(html_document: HtmlDocument) -> None:
    """
    Write style on report_html file
    :param html_document:
    :return:
    """
    html_document.open_style()
    html_document.style_title()
    html_document.style_spacer_xs()
    html_document.style_spacer_md()
    html_document.style_spacer_lg()
    html_document.style_page_break()
    html_document.style_resize()
    html_document.class_font_size(14)
    html_document.close_style()


def write_head(html_document: HtmlDocument) -> None:
    """
    Write head on report_html file
    :param html_document:
    :return:
    """
    html_document.open_head()
    html_document.meta()
    html_document.link_bootstrap()
    write_style(html_document)
    html_document.close_head()


def write_main_header(html_document: HtmlDocument) -> None:
    """
    Write main header of report_html file
    :param html_document:
    :return:
    """
    html_document.open_html_document()
    write_head(html_document)
    html_document.open_body()
    logo_kununu = convert_path_image_64(get_project_path() + cons.path_image_kununu)
    html_document.insert_image(logo_kununu, class_txt="\"spacer--xs\"", height=51,
                               width=224)


def insert_data_header(table: HtmlTable, dict_header: dict) -> None:
    """
    Write header of the table
    :param table:
    :param dict_header
    :return:
    """
    table.open_thead()
    table.open_row()
    for i in list(dict_header.keys()):
        table.open_cell_head(dict_header[i])
        table.html_table = table.html_table + i
        table.close_cell_head()
    table.close_row()
    table.close_thead()


def insert_data_table(table: HtmlTable, data: list) -> None:
    """
    Write data into the table of report_html file
    :param table:
    :param data:
    :param company_id:
    :return:
    """
    try:
        for i in data:
            table.open_row()
            for j in i.keys():
                table.open_cell(color=define_color(j, i[j]))
                table.html_table = table.html_table + i[j]
                table.close_cell()
            table.close_row()

    except Exception as e:
        logger.error(msg="Error into dictionary of the interface:  %s" % e)
        sys.exit(1)


def open_table_on_file(table: HtmlTable) -> None:
    """
    Open the table into report_html file
    :param table: table of report_html
    :return:
    """
    table.open()


def build_body_table(table: HtmlTable, data: list) -> None:
    """
    Write the data into the table of report_html file
    :param table: table of report_html file
    :param data: dictionary with the data
    :param company_id: company_id string
    :return:
    """
    table.open_body()
    insert_data_table(table, data)
    table.close_body()


def write_title(html_document: HtmlDocument, title: str, cw: int, year: int) -> None:
    """
    Wrtite title of the document
    :param html_document: HTML document
    :param title: string with the title
    :param cw: current week
    :param year: current year of the report generation
    :return:
    """
    html_document.write_title(title, cw, year, class_txt="spacer--md")


def write_subtitle(html_document: HtmlDocument, subtitle: str, page_break: bool) -> None:
    """
    Wrtite subtitle of the document
    :param html_document: HTML document
    :param subtitle: string with the subtitle
    :param page_break: boolean for page break in report_html file
    :return:
    """
    html_document.write_subtitle(subtitle, page_break, class_txt="spacer--lg")


def close_table_on_file(table: HtmlTable) -> None:
    """
    Close the table on  file
    :param table: type table
    :return:
    """
    table.close()


def build_table(html_document: HtmlDocument, data: list, list_header: dict) -> None:
    """
    Build the table
    :param html_document:
    :param data:
    :param company_id:
    :return:
    """
    table = HtmlTable()
    open_table_on_file(table)
    insert_data_header(table, list_header)
    build_body_table(table, data)
    close_table_on_file(table)
    html_document.html_doc = html_document.html_doc + table.html_table


def close_document(html_document: HtmlDocument) -> None:
    """
    Close the report_html document
    :return:
    """
    html_document.close_body()
    html_document.close()
