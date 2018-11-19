__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import re
from crossval.moses_runner import MosesRunner
import unittest
from config import TEST_DATA_DIR, moses_options
import os


class TestMosesRun(unittest.TestCase):

    def setUp(self):
        self.input_file = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        self.output_file = os.path.join(TEST_DATA_DIR, "moses_test_output")
        self.moses_opts = moses_options

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        moses_log = os.path.join(os.path.dirname(__file__), "moses.log")
        opencog_log = os.path.join(os.path.dirname(__file__), "opencog.log")
        if os.path.exists(moses_log):
            os.remove(moses_log)
        if os.path.exists(opencog_log):
            os.remove(opencog_log)

    def test_run_moses_happy_path(self):
        moses_runner = MosesRunner(self.input_file, self.output_file, self.moses_opts)

        self.assertEqual(moses_runner.run_moses()[0], 0)  # successfully ran moses

    def test_run_moses_error_path(self):
        tweaked_options = self.moses_opts + "-xyz"  # this is done to make moses deliberately fail
        moses_runner = MosesRunner(self.input_file, self.output_file, tweaked_options)

        self.assertNotEqual(moses_runner.run_moses()[0], 0)

        self.assertNotEqual("", moses_runner.run_moses()[2])  # make sure there is an error output

    def test_format_combo(self):
        moses_runner = MosesRunner(self.input_file, self.output_file, self.moses_opts)
        moses_runner.run_moses()
        test_combo_file = os.path.join(TEST_DATA_DIR, self.output_file)

        moses_runner.format_combo(test_combo_file)

        test_regex = re.compile(r"(.+),(\d+)")

        with open(test_combo_file, "r") as f:
            for i, line in enumerate(f):
                if i == 0: # header
                    self.assertEqual(line.strip(), "model,complexity")
                else:
                    self.assertIsNotNone(test_regex.match(line.strip()))


if __name__ == "__main__":
    unittest.main()
