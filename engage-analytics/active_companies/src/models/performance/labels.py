"""
Scripts to Build Labels for further analysis
"""
import logging
import pandas as pd

logger = logging.getLogger()


class ConfusionMatrixLabel:
    """
    Class with methods to define labels for multiple proporses
    """

    @staticmethod
    def active_companies(all_companies: pd.DataFrame, true_companies: pd.DataFrame, selected_companies: pd.DataFrame,
                         label_name_as_truth: str = 'label_true',
                         label_name_to_validate: str = 'label_algorithm',
                         selected_companies_location: str = 'company_id') -> pd.DataFrame:
        """
        Creates a label with the same dimension for companies present in engage
        :param all_companies DataFrame containing all engage companies info
        :param selected_companies_location: name of the column on data_connection frame with companies on selected_companies
        :param label_name_to_validate: name of the label of the method we are trying to validate
        :param label_name_as_truth: name of the label that we considered should be the result of the method
        :param true_companies: active companies we are trying to compare to
        :param selected_companies: active companies selected by the method we want to validate
        :return: data_connection frame with labels of the both methods, and id and name of all companies
        """
        # Join all ids from incoming algorithms
        all_incoming_ids = list(set(true_companies["id"].tolist() + selected_companies["company_id"].tolist()))

        all_companies = all_companies[all_companies["id"].isin(all_incoming_ids)]

        all_companies[label_name_as_truth] = 0
        if true_companies.shape[0] >= 1:
            all_companies.loc[all_companies.id.isin(true_companies['id']), label_name_as_truth] = 1
        all_companies[label_name_to_validate] = 0
        all_companies.loc[all_companies.id.isin(selected_companies[selected_companies_location]),
                          label_name_to_validate] = 1

        return all_companies
