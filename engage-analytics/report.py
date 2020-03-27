import argparse
import logging.config
import sentiment_analysis.src.report.cons_report as cons

from utils.gcloud.storage import Storage
from sentiment_analysis.src.report.write_report import WriteReport
from sentiment_analysis.src.report.interface_report import InterFaceReport
from sentiment_analysis.src.report.preparation_report import PreparationReport
from utils.utilities import get_last_week, set_log_level, get_project_path
from utils.data_connection.redis_manager import RedisManager
from utils.data_connection.factory.redis_factory import RedisFactory

logging.config.fileConfig("%s/logging.ini" % get_project_path())
set_log_level()
logger = logging.getLogger()


def preparation_report(period: dict, weeks_analyze: int, company_id: str,
                       redis_manager: RedisManager) -> PreparationReport:
    """
    Take the data from db and redis
    :param period: dict containing the respective period with the following keys: {start_year, start_week, end_year, end_week}
    :param weeks_analyze: number of weeks to analyze
    :param company_id: company_id
    :param redis_manager: Redis manager
    :return: the data for make the report from redis and from db
    """
    prep_report = PreparationReport(period=period,
                                    weeks_analyze=weeks_analyze,
                                    company_id=company_id,
                                    redis_manager=redis_manager
                                    )
    prep_report.process_data()

    return prep_report


def make_interface(prep_report: PreparationReport) -> InterFaceReport:
    """
    Create an interface for capture the data needed
    :param prep_report: Data from DB and redis
    :return: dict with the data needed to make report
    """
    interface = InterFaceReport(topics=prep_report.topics,
                                surveys=prep_report.replies,
                                company_id=prep_report.company_id,
                                weeks=prep_report.weeks,
                                g_client=prep_report.g_client,
                                api_source_manager=prep_report.api_source_manager)

    interface.process_interface()
    interface.word_cloud()

    return interface


def make_report(interface: InterFaceReport, period: dict) -> None:
    """
    Make interface for report
    :param interface: Data needed only for interface (dict)
    :param period: dict containing the respective period with the following keys: {start_year, start_week, end_year, end_week}
    :return: make the interface to filter the data needed to make report
    """
    write_report = WriteReport(period=period)
    write_report.write_header()

    write_report.write_table(cons.subtitle_sr, False, interface.table_surveys_replies,
                             cons.columns_names_surveys_reply_percentage)

    write_report.write_image(cons.subtitle_sr_wc, True, interface.image_base64_sr, interface.table_surveys_replies)

    write_report.write_table(cons.subtitle_topics, True, interface.table_topics,
                             cons.columns_names_topics_percentage)
    write_report.write_table(cons.subtitle_topics_comments, True, interface.table_topic_comment,
                             cons.columns_names_topics_percentage)
    write_report.write_image(cons.subtitle_topics_wc, True, interface.image_base64_topics, interface.table_topics)

    target_dir = get_project_path() + cons.output_pdf_file

    write_report.save_pdf(target_week, target_year, target_dir, company_id=None)
    Storage.upload_files(target_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run sentiment analysis for survey replies and topics')
    parser.add_argument('--year', type=int, help='year of the survey')
    parser.add_argument('--week', type=int, help='week of the survey')
    parser.add_argument('--weeks_to_analyze', type=int, help='number of weeks to agglomerate the scores', default=1)
    parser.add_argument('--company_id', type=str, help='target company id')
    args = parser.parse_args()
    target_year = args.year
    target_week = args.week
    weeks_to_analyze = args.weeks_to_analyze
    company_id = args.company_id

    if target_week is None or target_year is None:
        target_year, target_week = get_last_week()

    period = {"start_year": target_year,
              "start_week": target_week,
              "end_year": target_year,
              "end_week": target_week}

    redis_manager = RedisFactory.build()

    report = preparation_report(period=period,
                                weeks_analyze=weeks_to_analyze,
                                redis_manager=redis_manager,
                                company_id=company_id)

    report_interface = make_interface(prep_report=report)

    make_report(interface=report_interface, period=period)
