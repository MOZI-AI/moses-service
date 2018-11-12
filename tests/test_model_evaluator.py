__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from crossval.model_evaluator import ModelEvaluator
from tests import DATA_DIR
import os


class TestModelEvaluator(unittest.TestCase):
    def setUp(self):
        self.test_combo = os.path.join(DATA_DIR, "test_combo")
        self.input_file = os.path.join(DATA_DIR, "bin_truncated.csv")

    def test_run_eval_happy_path(self):
        model_eval = ModelEvaluator(None, None, None, "case")

        matrix = model_eval.run_eval(self.test_combo, self.input_file)

        with open(self.test_combo, "r") as fp:
            rows = sum(1 for line in fp) - 1
        with open(self.input_file, "r") as fp:
            cols = sum(1 for line in fp) - 1

        self.assertEqual(matrix.shape, (rows, cols))