__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import numpy as np
import pandas as pd
import subprocess
import logging
import os

class ModelEvaluator:
    """
    This is class evaluates programs that are output by MOSES and scores them against test and training data
    """

    def __init__(self, model_file, test_file, train_file, target_feature):
        self.model = model_file
        self.test = test_file
        self.train = train_file
        self.target_feature = target_feature
        self.logger = logging.getLogger("mozi_snet")

    def run_eval(self, combo_file, input_file):
        """
        Takes a combo file containing MOSES programs and an input file on which it evaluates each program on.
        :param
        combo_file: the location of the combo file
        :param input_file: the location of the input file
        :return: matrix:
        nxm matrix where n is the number of models and m is the number of samples. the matrix contains the predicted
        output of each model on the sample
        """
        with open(combo_file, "r") as fp:
            num_models = sum(1 for line in fp) - 1  # the number of models

        with open(input_file, "r") as fp:
            num_samples = sum(1 for line in fp) - 1

        matrix = np.empty((num_models, num_samples), dtype=int)

        models_df = pd.read_csv(combo_file)

        models = models_df.model.values

        temp_eval_file = "eval_tmp"

        for i, model in enumerate(models):
            cmd = ["eval-table", "-i", input_file, "-c", model, "-o", temp_eval_file, "-u", self.target_feature]
            self.logger.debug("Evaluating model %s" % model)
            self.logger.debug("Eval table command: %s" % cmd)
            process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE)

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                matrix[i] = np.genfromtxt(temp_eval_file, skip_header=1, dtype=int)


            else:
                self.logger.error("The following error raised by eval-table %s" % stderr.decode("utf-8"))
                raise ChildProcessError("Eval-table run to this error: %s" % stderr.decode("utf-8"))

        # clean up temp file and log file
        os.remove(temp_eval_file)
        os.remove("eval-table.log")

        return matrix



