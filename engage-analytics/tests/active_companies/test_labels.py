import unittest
import pandas as pd

from active_companies.src.models.performance.labels import ConfusionMatrixLabel


class TestConfusionMatrixLabel(unittest.TestCase):

    def setup_active_companies(self):
        mock_all_companies = pd.DataFrame(
            index=range(20),
            columns=["id"]
        )
 #       print([str(uuid.uuid4()) for _ in range(10)])
        mock_true_companies = pd.DataFrame(
            index=range(20),
            columns=["id"]
        )

        mock_selected_companies = pd.DataFrame(
            index=range(20),
            columns=["company_id"]
        )
        return mock_all_companies, mock_true_companies, mock_selected_companies

    def teardown_active_companies(self, mock_all_companies, mock_true_companies,mock_selected_companies):
        del mock_all_companies, mock_true_companies,mock_selected_companies

    def test_active_companies(self):
        mock_all_companies, mock_true_companies, \
        mock_selected_companies = TestConfusionMatrixLabel.setup_active_companies(self)
        all_companies = ConfusionMatrixLabel.active_companies(mock_all_companies, mock_true_companies, \
        mock_selected_companies)
        assert 'label_true' in all_companies.columns.values
        assert 'label_algorithm' in all_companies.columns.values
        assert isinstance(all_companies, pd.DataFrame)
        yield
        TestConfusionMatrixLabel.teardown_active_companies(self, mock_all_companies, mock_true_companies,mock_selected_companies)
