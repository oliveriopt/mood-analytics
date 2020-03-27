import os
import pdfkit

from sentiment_analysis.src.report_html.write_html import *


class WriteReport:

    def __init__(self, period: dict):
        """
        Object responsible for writing the HTML report.
        :param period: dict containing the respective period with the following keys: {start_year, start_week, end_year, end_week}
        """
        self.html_document = HtmlDocument()
        self.period = period
        self.target_year = self.period.get("end_year")
        self.target_week = self.period.get("end_week")

    def write_header(self) -> None:
        """
        Write header of report_html document
        :return: Header of the file
        """
        write_main_header(self.html_document)
        write_title(self.html_document, cons.title, self.target_week, self.target_year)

    def write_table(self, subtitle: str, break_page: bool, data_for_table: list, column_names: list) -> None:
        """
        Write table of report_html document
        :param subtitle: subtitle of the part
        :param break_page: boolean for break page
        :param data_for_table: data to print in report_html document
        :param column_names: column names to print
        :return: Table with data
        """
        if data_for_table:
            write_subtitle(self.html_document, subtitle, break_page)
            build_table(self.html_document, data_for_table, column_names)

        else:
            write_subtitle(self.html_document, cons.subtitle_sr_no_comments, break_page)

    def write_image(self, subtitle: str, break_page: bool, image_base_64: str, data_for_table: list) -> None:
        """
        Write image of report_html document
        :param subtitle: subtitle of the part
        :param break_page: boolean for break page
        :param image_base_64: path of the file
        :param data_for_table: data to print in report_html document
        :return: Image of the data
        """
        if data_for_table:
            write_subtitle(self.html_document, subtitle, break_page)
            self.html_document.insert_image(image_base_64, class_txt="\"spacer--lg\"", height=None, width=None)

    def save_pdf(self, target_week: int, target_year: int, target_dir: str, company_id=None) -> None:
        """
        Print to pdf file
        :param target_week: week to analyze
        :param target_year: year to analyze
        :param target_dir: dir where is the report_pdf saved
        :param company_id: string of company id
        :return: save the pdf into file
        """

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        f = open("../temp.html", "w")
        f.write(self.html_document.html_doc)
        f.close()

        options = {
            'margin-bottom': '19.05mm',
            'footer-right': '[page] of [topage]'
        }
        name_company = ""
        if company_id is None:
            name_company = "kununu"
        pdfkit.from_file('../temp.html', target_dir + "engage_insights_w" + str(target_week) + "_" + str(
            target_year) + "_" + name_company + ".pdf",
                         options=options)
        os.remove("../temp.html")
