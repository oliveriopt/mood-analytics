"""
Module with the classes and objects related to the identification of the active companies
"""
import logging
import numpy
import pandas as pd
import utils.data_connection.constant_variables_db as cons

from datetime import date
from utils.data_connection.api_data_manager import APISourcesFetcher
from utils.utilities import get_iterations_year_week, get_today_year_week

logger = logging.getLogger()


class OliverClassifierTimeSeries:
    """
    Class that identifies the active companies
    https://confluence.xing.hh/display/kununu/Active+Companies+Second+Approach+%3A+Time+Series+Analysis
    """

    def __init__(self, api_sources_fetcher: APISourcesFetcher, time_trial=cons.TIME_TRIAL,
                 delay_weeks=cons.DELAY_WEEKS):
        """
        Constructor to the Classifier of Active Companies using Time Series Basic Logic
        :param api_sources_fetcher: object to get information from API DB
        :param time_trial: time trial to be considered (filter for valid companies)
        :param delay_weeks: weeks to considered to filter valid companies
        """
        self.__companies = None
        self.__users = None
        self.__survey_moods = None
        self.__time_trial = time_trial
        self.__delay_weeks = delay_weeks
        self.__api_data_fetcher = api_sources_fetcher

        self.__test_companies = cons.TEST_COMPANIES
        self.__viable_companies = None
        self.__viable_user_per_company = None
        self.__viable_users = None
        self.__viable_surveys = None

    # getter and setters for the data we want to use
    @property
    def existence_days(self) -> int:
        return self.__time_trial

    @property
    def viable_companies(self) -> pd.DataFrame:
        return self.__viable_companies

    @property
    def viable_users(self) -> pd.DataFrame:
        return self.__viable_users

    @property
    def viable_surveys(self) -> pd.DataFrame:
        return self.__viable_surveys

    @existence_days.setter
    def existence_days(self, new_existence_days) -> None:
        self.__time_trial = new_existence_days

    @property
    def delay_weeks(self) -> int:
        return self.__delay_weeks

    @delay_weeks.setter
    def delay_weeks(self, new_delay_weeks) -> None:
        if new_delay_weeks > 10:
            logger.error(msg="No more than 10 delay gap is allowed")
            self.__delay_weeks = 10
        else:
            self.__delay_weeks = new_delay_weeks

    @property
    def companies(self) -> pd.DataFrame:
        return self.__companies

    def set_companies(self) -> None:
        self.__companies = self.__api_data_fetcher.get_companies_info()

    @property
    def users(self) -> pd.DataFrame:
        return self.__users

    def set_users(self) -> None:
        self.__users = self.__api_data_fetcher.get_companies_users()

    @property
    def test_companies(self) -> list:
        return self.__test_companies

    @property
    def surveys_mood(self) -> pd.DataFrame:
        return self.__survey_moods

    def set_surveys_mood(self):
        self.__survey_moods = self.__api_data_fetcher.get_surveys_mood()

    def _prepare_viable_companies(self) -> None:
        """
        Step 1 of the algorithm - Filter the test companies
        :return:  viable
        """

        if self.__companies.empty:
            logger.warning(msg="Services: Active Companies Table Empty from Python Code")
            raise Exception("Services: Active Companies Table Empty from Python Code")

        # Filter the test companies
        viable_companies = self.__companies[~self.__companies.domain.isin(self.__test_companies)]
        # Filter the companies enabled
        viable_companies = viable_companies[viable_companies['is_enabled'] == 1]

        # Filter the companies deleted
        viable_companies = viable_companies[viable_companies.deleted_at.isna()]

        # Companies with more than x days of existence
        days_of_existence = pd.to_datetime(date.today().strftime("%Y-%m-%d 00:00:00")) - pd.to_datetime(
            viable_companies['created_at'])
        viable_companies = viable_companies[days_of_existence.astype('timedelta64[D]') >= self.__time_trial]

        self.__viable_companies = viable_companies

        logging.info("ALREADY PREPARED VIABLE COMPANIES")

    @staticmethod
    def companies_with_more_than_5_users(viable_users: pd.DataFrame, viable_companies: pd.DataFrame) -> tuple:
        """
        Filters viable users based having in mind companies with >= 5 users
        :param viable_users: potential viable users
        :param viable_companies: potential viable companies
        :return:
        """
        company_group_by_users_number = viable_users.groupby('company_id')['user_id'].count()
        company_group_by_users_number = company_group_by_users_number[company_group_by_users_number >= 5]
        viable_user_per_company = company_group_by_users_number
        viable_companies = viable_companies[
            viable_companies.id.isin(company_group_by_users_number.index)]
        return viable_user_per_company, viable_users[viable_users.company_id.isin(viable_companies['id'].values)]

    def _prepare_viable_users(self, viable_companies: pd.DataFrame) -> None:
        """
        Step 2 of the algorithm -  Identify the number of user of each company
        :param viable_companies: viable companies, already processed
        :return:
        """
        if self.__users.empty:
            logger.warning(msg="Services: Active Companies Table Empty from Python Code")
            raise Exception("Services: Active Companies Table Empty from Python Code")

        # Filter the enabled users
        viable_users = self.__users[self.__users['is_enabled'] == 1]

        # Filter the nan users
        viable_users = viable_users[~viable_users.user_id.isna()]

        # Filter the deleted users
        viable_users = viable_users[viable_users.deleted_at.isna()]

        if self.__viable_companies is not None:
            # Merging viable users
            viable_users = viable_users[viable_users.company_id.isin(viable_companies['id'])]

        # Filter the number of companies with more than 5 users
        self.__viable_user_per_company, self.__viable_users = OliverClassifierTimeSeries.companies_with_more_than_5_users(
            viable_users=viable_users,
            viable_companies=self.__viable_companies)
        logging.info("ALREADY PREPARED VIABLE USERS")

    @staticmethod
    def filter_surveys_by_iteration_gap(viable_surveys: pd.DataFrame, iteration_gap=2) -> numpy.ndarray:
        """
        Filter viable surveys by iteration gap, number of survey replies in the last "iteration_gap" weeks
        :param viable_surveys:
        :param iteration_gap:
        :return:
        """
        # Filter companies that have more than iteration_gap survey replies in the iterations range
        viable_surveys_grouped = viable_surveys.groupby(['company_id', viable_surveys['created_at'].dt.week],
                                                        as_index=False).count()
        viable_surveys_grouped = viable_surveys_grouped.groupby("company_id").filter(
            lambda x: x['company_id'].count() >= iteration_gap)

        return viable_surveys_grouped['company_id'].unique()

    def _surveys_steps(self, viable_users: pd.DataFrame, year: int = None, week: int = None, iteration_gap=2) -> tuple:
        """
        Step 3 of the algorithm - Filters by participation delay
        :param viable_users viable users after filtering viable companies
        :param year year for which we want the valid surveys
        :param week limit week from which we want the valid surveys
        :return:
        """

        if self.__survey_moods.empty:
            logger.warning(msg="Services: Active Companies Table Empty from Python Code")
            raise Exception("Services: Active Companies Table Empty from Python Code")

        # Filter surveys with only viable user_id
        viable_surveys = self.__survey_moods[self.surveys_mood.user_id.isin(viable_users['user_id'].values)]
        # Merge by column the surveys with the respective company
        # Filter surveys on viable users
        viable_surveys = pd.merge(viable_surveys, viable_users[['user_id', 'company_id']], on='user_id')

        # Get iterations year-week based on received parameters
        first_iteration_year, first_iteration_week, last_iteration_year, last_iteration_week = get_iterations_year_week(
            year=year, week=week, delay=iteration_gap)

        # Filter by viable surveys within the iterations range
        viable_surveys = viable_surveys[
            (viable_surveys['created_at'].dt.week >= first_iteration_week) &
            (viable_surveys['created_at'].dt.week <= last_iteration_week) &
            (viable_surveys['created_at'].dt.year >= first_iteration_year) &
            (viable_surveys['created_at'].dt.year >= last_iteration_year)]

        self.__viable_surveys = viable_surveys

        viable_company_ids = OliverClassifierTimeSeries.filter_surveys_by_iteration_gap(viable_surveys=viable_surveys,
                                                                                        iteration_gap=iteration_gap)
        return viable_company_ids, last_iteration_year, last_iteration_week

    def identify_active_companies(self) -> tuple:
        """
        Run all the steps of the company
        :return:
        """
        year, week = get_today_year_week()
        try:
            self.set_companies()
            self._prepare_viable_companies()

            self.set_users()
            self._prepare_viable_users(viable_companies=self.__viable_companies)

            self.set_surveys_mood()
            selected_companies_id, last_year, last_week = self._surveys_steps(viable_users=self.__viable_users,
                                                                              year=year,
                                                                              week=week)

            # Matching ids with company names
            companies_names = self.__viable_companies[self.__viable_companies.id.isin(selected_companies_id)][
                ['id', 'name']]

            if companies_names.empty:
                logger.warning(msg="Services: Active Companies Table Empty from Python Code")
                raise Exception("Services: Active Companies Table Empty from Python Code")
        except Exception as e:
            logger.warning(msg=str(e))
            return pd.DataFrame(), year, week

        return companies_names, year, week
