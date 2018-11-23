__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os
import unittest

import pandas as pd
from sklearn.model_selection import train_test_split

from crossval.model_evaluator import ModelEvaluator
from config import TEST_DATA_DIR


class TestModelEvaluator(unittest.TestCase):
    def setUp(self):
        self.test_combo = os.path.join(TEST_DATA_DIR, "test_combo")
        self.input_file = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")

    def test_run_eval_happy_path(self):
        model_eval = ModelEvaluator("case")

        test_df = pd.read_csv(self.test_combo)
        matrix = model_eval.run_eval(test_df, self.input_file)

        with open(self.test_combo, "r") as fp:
            rows = sum(1 for line in fp) - 1
        with open(self.input_file, "r") as fp:
            cols = sum(1 for line in fp) - 1

        self.assertEqual(matrix.shape, (rows, cols))

    def test_score_models(self):
        df = pd.read_csv(self.input_file)

        test_file = os.path.join(TEST_DATA_DIR, "temp_test.csv")
        train_file = os.path.join(TEST_DATA_DIR, "temp_train.csv")
        temp_model = os.path.join(TEST_DATA_DIR, "temp_model.csv")

        train, test = train_test_split(df, test_size=0.3)

        train.to_csv(train_file, index=False)
        test.to_csv(test_file, index=False)

        # make a copy of test_combo and use that for the test
        temp_file = os.path.join(TEST_DATA_DIR, temp_model)
        with open(self.input_file) as f:
            with open(temp_file, "w") as fp:
                for line in f:
                    fp.write(line)

        model_eval = ModelEvaluator("case")

        test_df = pd.read_csv(self.test_combo)
        matrix = model_eval.run_eval(test_df, test_file)

        scored_matrix = model_eval.score_models(matrix, test_file)

        self.assertEqual(scored_matrix.shape, (matrix.shape[0], 5))

        print(scored_matrix)

        os.remove(test_file)
        os.remove(train_file)
        os.remove(temp_model)


if __name__ == '__main__':
    unittest.main()
