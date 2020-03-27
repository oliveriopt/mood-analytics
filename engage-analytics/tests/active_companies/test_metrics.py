import unittest
import pandas as pd

from active_companies.src.models.performance.metrics import Evaluation


class TestEvaluation(unittest.TestCase):

    def setup_accuracy(self):
        df_100 = pd.DataFrame(
            0,
            index=range(20),
            columns=['label_true', 'label_algorithm']
        )

        df_0 = pd.DataFrame(
            index=range(20),
            columns=['label_true', 'label_algorithm']
        )
        df_0['label_true'] = 0
        df_0['label_algorithm'] = 1
        return df_100, df_0

    def tearDown_accuracy(self, df_100, df_0):
        del df_100
        del df_0

    def test_accuracy(self):
        test_df_100, test_df_0 = TestEvaluation.setup_accuracy(self)
        acc_100 = Evaluation.accuracy(test_df_100)
        acc_0 = Evaluation.accuracy(test_df_0)
        assert isinstance(acc_100, float)
        assert isinstance(acc_0, float)
        assert acc_100 == 100.00
        assert acc_0 == 0.00
        TestEvaluation.tearDown_accuracy(self, test_df_100, test_df_0)
