"""
Modules that can determine diferent metrics to evaluate an algorithm sucess
"""
import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date

logger = logging.getLogger()
sns.set(style="darkgrid")


class ConfusionMatrix:
    """
    Class with method for each algorithm that defines
    """
    @staticmethod
    def active_companies(all_companies, true_companies, selected_companies):
        """
        This function will label all the companies present... as active [1] or not active [0]
        With this function we will have all the elements of an confusion matrix
        :param true_companies: companies actually answering surveys last week
        :param all_companies: the list with ids of all companies present.. depending of the problems can be the
        companies present on that week or all the time, depends of the design of the validation part
        :param selected_companies: companies identified by the algorithm
        :return: labels, true_positives, true_negatives, false_positives, false_positives
        """

        # Each companies present on the database, will considered
        # Note all_companies is all the companies present in that time frame... actually with more
        # than 5 surveys answered, with no more complex analysis
        # all the dataframe as an input should have ['id', name] as columns

        # Label accordingly with true_companies
        all_companies['label_truth'] = 0
        if true_companies.shape[0] >= 1:
            all_companies.loc[all_companies.id.isin(true_companies['id']), 'label_truth'] = 1
        all_companies['label_algorithm'] = 0
        all_companies.loc[all_companies.id.isin(selected_companies['id']), 'label_algorithm'] = 1

        true_positives = all_companies[(all_companies['label_truth'] == 1) & (all_companies['label_algorithm'] == 1)]
        true_negatives = all_companies[(all_companies['label_truth'] == 0) & (all_companies['label_algorithm'] == 0)]
        false_negatives = all_companies[(all_companies['label_truth'] == 1) & (all_companies['label_algorithm'] == 0)]
        false_positives = all_companies[(all_companies['label_truth'] == 0) & (all_companies['label_algorithm'] == 1)]

        return all_companies[
                   ['label_truth', 'label_algorithm']], true_positives, true_negatives, false_negatives, false_positives


class StatsLastWeek:

    @staticmethod
    def companies(companies_last_week, surveys_last_week, users_last_week):
        """
        Stats related with all parameter
        :param companies_last_week:
        :param surveys_last_week:
        :param users_last_week:
        :return: days_of_existence
        """

        # Compute numbers of users per_companies
        # Clean users first
        # Filter the enabled users
        users_last_week = users_last_week[users_last_week['is_enabled'] == 1]

        # Filter the nan users
        users_last_week = users_last_week[~users_last_week.user_id.isna()]

        # Filter the deleted users
        users_last_week = users_last_week[users_last_week.deleted_at.isna()]

        # Having Only for the companies
        # Determine days_of_existence
        days_of_existence = pd.to_datetime(date.today().strftime("%Y-%m-%d 00:00:00")) - pd.to_datetime(
            companies_last_week['created_at'])

        # Determine number of users per company
        nr_users_per_company = users_last_week.groupby('company_id')['user_id'].count()

        viable_surveys = surveys_last_week[surveys_last_week.user_id.isin(users_last_week.user_id)]
        viable_surveys_grouped = pd.merge(viable_surveys, users_last_week[['user_id', 'company_id']], on='user_id')
        viable_surveys_grouped = viable_surveys_grouped.groupby('company_id')['user_id'].count()

        # Determine normal rate, for that i have to determine number total of weeks
        survey_weights = 100 * viable_surveys_grouped / viable_surveys_grouped.sum()

        stats = companies_last_week[['id', 'name']]
        stats = pd.concat([stats, days_of_existence], axis=1)
        stats.columns = ['company_id', 'company_name', 'days_of_existence']
        stats2 = pd.concat([nr_users_per_company, survey_weights], axis=1)
        stats2 = stats2.reset_index()
        stats2.columns = ['company_id', 'nr_of_users', 'surveys_weights']
        stats = pd.merge(stats, stats2, on='company_id')

        return stats


class Stats:

    @staticmethod
    def companies_survey_rates(companies, surveys, company_users, total_weeks=None):
        # Ok so now i have all the companies
        company_users = company_users[company_users['is_enabled'] == 1]

        # Filter the nan users
        company_users = company_users[~company_users.user_id.isna()]

        # Filter the deleted users
        company_users = company_users[company_users.deleted_at.isna()]
        # Select users from companies
        selected_users = company_users[company_users.company_id.isin(companies['id'])]
        selected_surveys = surveys[surveys.user_id.isin(selected_users['user_id'])]

        # Answering Rate
        selected_surveys = pd.merge(selected_surveys, selected_users[['user_id', 'company_id']], on="user_id")
        selected_surveys = selected_surveys.groupby('company_id')['user_id'].count()
        selected_surveys = selected_surveys / total_weeks
        selected_surveys = selected_surveys.reset_index()
        selected_surveys.columns = ['company_id', 'surveys_rate']
        return selected_surveys


class Evaluation:

    @staticmethod
    def accuracy(labels: pd.DataFrame, label_name_as_truth: str = 'label_true',
                 label_name_to_validate: str = 'label_algorithm') -> float:
        """
        Determine the accuray
        :param labels:
        :param label_name_as_truth:
        :param label_name_to_validate:
        :return:
        """

        correctly_labelled = labels[labels[label_name_as_truth] == labels[label_name_to_validate]].shape[0]
        all_labelled = labels.shape[0]

        return 100 * correctly_labelled / all_labelled

    @staticmethod
    def stats_per_week_companies(dict_results, test_name="Oliver Classifier from Cumulative Week Test", save_path=""):

        false_positives_avg_users = []
        nr_false_positives = []
        false_positives_avg_rate = []
        false_positives_avg_days = []
        false_positives_avg_surveys_weight = []

        false_negatives_avg_users = []
        nr_false_negatives = []
        false_negatives_avg_rate = []
        false_negatives_avg_days = []
        false_negatives_avg_surveys_weight = []

        for week in dict_results.keys():
            first_unit = dict_results[week]
            positives = first_unit['stats_false_positives']
            nr_false_positives.append(positives.shape[0])
            false_positives_avg_users.append(positives['nr_of_users'].mean())
            false_positives_avg_rate.append(positives['surveys_rate'].mean())
            false_positives_avg_days.append(positives['days_of_existence'].dt.days.mean())
            false_positives_avg_surveys_weight.append(positives['surveys_weights'].mean())

            negatives = first_unit['stats_false_negatives']
            nr_false_negatives.append(negatives.shape[0])
            false_negatives_avg_users.append(negatives['nr_of_users'].mean())
            false_negatives_avg_rate.append(negatives['surveys_rate'].mean())
            false_negatives_avg_days.append(negatives['days_of_existence'].dt.days.mean())
            false_negatives_avg_surveys_weight.append(negatives['surveys_weights'].mean())

        # Graphs Positives
        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), nr_false_positives, ax=axes)
        plt.title("Number of False Positives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Number of False Positives")
        plt.savefig(save_path + "/graphs/False Positives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_positives_avg_users, ax=axes)
        plt.title("Average Number of Users of False Positives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Number of Users")
        plt.savefig(save_path + "/graphs/Average Number of Users False Positives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_positives_avg_rate, ax=axes)
        plt.title("Average Rate of Answered Surveys of False Positives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Rate of Answered Surveys")
        plt.savefig(save_path + "/graphs/Average Rate of Answered Surveys of False Positives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_positives_avg_days, ax=axes)
        plt.title("Average Days of Companies Existence of False Positives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Days of Companies Existence ")
        plt.savefig(save_path + "/graphs/Average Days of Companies Existence of False Positives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_positives_avg_surveys_weight, ax=axes)
        plt.title("Average Surveys Weights of False Positives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Surveys Weights")
        plt.savefig(save_path + "/graphs/Average Surveys Weights of False Positives " + test_name + ".jpg")

        # Graphs Negatives
        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), nr_false_negatives, ax=axes)
        plt.title("Number of False Negatives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Number of False Negatives")
        plt.savefig(save_path + "/graphs/False Negatives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_negatives_avg_users, ax=axes)
        plt.title("Average Number of Users of False Negatives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Number of Users")
        plt.savefig(save_path + "/graphs/Average Number of Users False Negatives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_negatives_avg_rate, ax=axes)
        plt.title("Average Rate of Answered Surveys of False Negatives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Rate of Answered Surveys")
        plt.savefig(save_path + "/graphs/Average Rate of Answered Surveys of False Negatives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_negatives_avg_days, ax=axes)
        plt.title("Average Days of Companies Existence of False Negatives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Days of Companies Existence ")
        plt.savefig(save_path + "/graphs/Average Days of Companies Existence of False Negatives " + test_name + ".jpg")

        f, axes = plt.subplots(1, 1, figsize=(10, 7))
        sns.lineplot(np.arange(1, len(dict_results.keys()) + 1), false_negatives_avg_surveys_weight, ax=axes)
        plt.title("Average Surveys Weights of False Negatives per Week of " + test_name)
        plt.xlim([1, len(dict_results.keys()) + 1])
        plt.xlabel("Week Number")
        plt.ylabel("Average Surveys Weights")
        plt.savefig(save_path + "/graphs/Average Surveys Weights of False Negatives " + test_name + ".jpg")