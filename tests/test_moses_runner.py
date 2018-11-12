__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import re
from crossval.moses_runner import MosesRunner
import unittest
from tests import DATA_DIR
import os


class TestMosesRun(unittest.TestCase):

    def setUp(self):
        self.input_file = os.path.join(DATA_DIR, "bin_truncated.csv")
        self.output_file = os.path.join(DATA_DIR, "moses_test_output")
        self.moses_opts = "-j8 --balance=1 -m 1000 -W1 --output-cscore=1 --result-count 100 " \
                          "--reduct-knob-building-effort=1 --hc-widen-search=1 --enable-fs=1 --fs-algo=simple " \
                          "--fs-target-size=4 --hc-crossover-min-neighbors=5000 --fs-focus=all --fs-seed=init " \
                          "--complexity-ratio=3 --hc-fraction-of-nn=.3 --hc-crossover-pop-size=1000"

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
        test_combo_file = os.path.join(DATA_DIR, self.output_file)

        moses_runner.format_combo(test_combo_file)

        test_regex = re.compile(r"(.+),(\d+)")

        with open(test_combo_file, "r") as f:
            for i, line in enumerate(f):
                if i == 0:  # make sure the formatted file has the correct header
                    self.assertEqual(line.strip(), "model,complexity")
                elif i == 1:  # check the first line, that will be enough to test
                    self.assertIsNotNone(test_regex.match(line.strip()))


if __name__ == "__main__":
    unittest.main()
