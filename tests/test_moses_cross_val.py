from crossval.filters.loader import get_filter
from models.objmodel import MosesModel, Score

__author__ = "Abdulrahman Semrie<xabush@singularitynet.io>"
import unittest
from models.dbmodels import Session
from config import TEST_DATA_DIR, moses_options, crossval_options
import os
import uuid
from crossval.moses_cross_val import CrossValidation
import pandas as pd
import glob
from sklearn.model_selection import train_test_split
from unittest.mock import MagicMock


class TestCrossValidation(unittest.TestCase):

    def setUp(self):
        dataset = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        session_id = str(uuid.uuid4())
        self.session = Session(session_id, moses_options, crossval_options, dataset, "abcd")

        self.train_file, self.test_file = os.path.join(TEST_DATA_DIR, "train_file"), os.path.join(TEST_DATA_DIR, "test_file")
        self.test_matrix = [[1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                            [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                            [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1],
                            [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1],
                            [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
                            [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1],
                            [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1]]

    def test_run_folds(self):
        filter_type = get_filter("accuracy")
        moses_cross_val = CrossValidation(self.session, None, filter_type, 0.7, TEST_DATA_DIR)
        mock = MagicMock()
        moses_cross_val.on_progress_update = mock

        moses_cross_val.run_folds()

        # Make sure the fold files exist
        fold_0 = os.path.join(TEST_DATA_DIR, "fold_0.csv")
        self.assertTrue(os.path.exists(fold_0))

        fold_df = pd.read_csv(fold_0)

        self.assertEqual(len(fold_df.columns), 12)

        self.assertEqual(mock.call_count, 3)

    def test_majority_vote(self):
        df = pd.read_csv(self.session.dataset)

        train_df, test_df = train_test_split(df, test_size=0.3)

        test_df.to_csv(self.test_file, index=False)
        filter_type = get_filter("accuracy")
        moses_cross_val = CrossValidation(self.session, None, filter_type, 0.4, TEST_DATA_DIR)
        moses_cross_val.test_file = self.test_file

        model_1 = MosesModel("and($ARDK, $AKFR)", 2)
        model_1.test_score = Score(0.8, 0.3, 0.7, 0.4, 0.2)
        model_1.train_score = Score(0, 0, 0, 0, 0)
        model_2 = MosesModel("or($RIPS, $RFS)", 3)
        model_2.train_score = Score(0, 0, 0, 0, 0)
        model_2.test_score = Score(0.5, 0.3, 0.6, 0.4, 0.2)
        model_3 = MosesModel("and($ARDK, $AKFR)", 2)
        model_3.train_score = Score(0, 0, 0, 0, 0)
        model_3.test_score = Score(0.4, 0.3, 0.2, 0.4, 0.2)

        models = {"fold_1": [model_1, model_2], "fold_2": [model_3]}
        moses_cross_val.result_models = models
        ensemble_df = moses_cross_val.majority_vote()

        self.assertEqual(ensemble_df.shape, (3, 6))

    def tearDown(self):
        if os.path.exists(self.test_file): os.remove(self.test_file)
        if os.path.exists(self.train_file): os.remove(self.train_file)
        if os.path.exists("feature_count.csv"): os.remove("feature_count.csv")

        moses_log = os.path.join(os.path.dirname(__file__), "moses.log")
        opencog_log = os.path.join(os.path.dirname(__file__), "opencog.log")
        if os.path.exists(moses_log):
            os.remove(moses_log)
        if os.path.exists(opencog_log):
            os.remove(opencog_log)

        for file in glob.glob("fold_[0-9].csv"):
            os.remove(file)

        if os.path.exists("ensemble.csv"):
            os.remove("ensemble.csv")


if __name__ == '__main__':
    unittest.main()
