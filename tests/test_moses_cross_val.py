__author__ = "Abdulrahman Semrie<xabush@singularitynet.io>"
import unittest
from models.dbmodels import Session
from config import TEST_DATA_DIR, moses_options, crossval_options
import os
import uuid
from crossval.moses_cross_val import CrossValidation
import pandas as pd
import glob


class TestCrossValidation(unittest.TestCase):

    def setUp(self):
        dataset = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        session_id = str(uuid.uuid4())
        self.session = Session(session_id, moses_options, crossval_options, dataset)

    def test_run_folds(self):
        moses_cross_val = CrossValidation(self.session, None, TEST_DATA_DIR)

        moses_cross_val.run_folds()

        # Make sure the fold files exist
        fold_0 = os.path.join(TEST_DATA_DIR, "fold_0.csv")
        self.assertTrue(os.path.exists(fold_0))

        fold_df = pd.read_csv(fold_0)

        self.assertEqual(len(fold_df.columns), 12)

    def tearDown(self):
        os.remove("test_file")
        os.remove("train_file")
        os.remove("feature_count.csv")
        moses_log = os.path.join(os.path.dirname(__file__), "moses.log")
        opencog_log = os.path.join(os.path.dirname(__file__), "opencog.log")
        if os.path.exists(moses_log):
            os.remove(moses_log)
        if os.path.exists(opencog_log):
            os.remove(opencog_log)

        for file in glob.glob("fold_[0-9].csv"):
            os.remove(file)


if __name__ == '__main__':
    unittest.main()
