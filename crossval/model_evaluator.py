__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import numpy as np
import pandas as pd
import subprocess
import logging
import os
from mlxtend.evaluate import scoring, mcnemar, mcnemar_table
import tempfile


class ModelEvaluator:
    """
    This is class evaluates programs that are output by MOSES and scores them against test and training data
    """

    def __init__(self, target_feature):
        self.target_feature = target_feature
        self.logger = logging.getLogger("mozi_snet")

    def run_eval(self, models_df, input_file):
        """
        Takes a combo file containing MOSES programs and an input file on which it evaluates each program on.
        :param
        combo_file: the location of the combo file
        :param input_file: the location of the input file
        :return: matrix:
        nxm matrix where n is the number of models and m is the number of samples. the matrix contains the predicted
        output of each model on the sample
        """

        input_df = pd.read_csv(input_file)

        models = models_df.model.values

        num_models, num_samples = models_df.shape[0], input_df.shape[0]
        matrix = np.empty((num_models, num_samples), dtype=int)

        temp_eval_file = tempfile.NamedTemporaryFile().name

        for i, model in enumerate(models):
            cmd = ["eval-table", "-i", input_file, "-c", model, "-o", temp_eval_file, "-u", self.target_feature]
            self.logger.debug("Evaluating model %s" % model)
            process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE)

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                matrix[i] = np.genfromtxt(temp_eval_file, skip_header=1, dtype=int)
            else:
                self.logger.error("The following error raised by eval-table %s" % stderr.decode("utf-8"))
                raise ChildProcessError(stderr.decode("utf-8"))

        return matrix

    def score_models(self, matrix, input_file):
        """
        Takes a matrix containing the predicted value of each model and a file to containing the actual target values
        It calculates the accuracy, recall, precision, f1 score and the p_value from mcnemar test of each model
        :param matrix: The input matrix
        containing the predicted values for each model. This the matrix returned by functions like run-eval
        :param input_file: this the test file containing the actual target values
        :return: matrix: returns an nx4 matrix where n is the number of model.
        """
        score_matrix = np.empty((matrix.shape[0], 5))

        df = pd.read_csv(input_file)
        target_value = df[self.target_feature].values
        null_value = np.zeros((len(target_value),))

        for i, row in enumerate(matrix):
            if np.unique(row).shape[0] == 1:
                # if the model is either true or false model, it has no significance. Hence assign -1 for each value
                neg_ar = np.empty((5,))
                neg_ar.fill(-1)
                score_matrix[i] = neg_ar
            else:
                scores = ModelEvaluator._get_scores(target_value, row)
                p_value = ModelEvaluator.mcnemar_test(target_value, row, null_value)
                scores.append(p_value)
                score_matrix[i] = np.array(scores)

        return score_matrix

    @staticmethod
    def _get_scores(target, predicted):
        """
        Helper method to get the accuracy, recall, precision and f1 scores
        :param target: a numpy array containing the target values
        :param predicted: a numpy array containing the predicted values
        :return: a numpy array containing the scores
        """
        recall = scoring(target, predicted, metric="recall")
        precision = scoring(target, predicted, metric="precision")
        accuracy = scoring(target, predicted, metric="accuracy")
        f_score = scoring(target, predicted, metric="f1")

        return [recall, precision, accuracy, f_score]

    @staticmethod
    def mcnemar_test(target, model_1_pred, model_2_pred):
        """
        Calculates p-value of the mcnemar test
        It builds a contingency table and uses that to calculate the p-value
        :param target: a numpy array that has the actual target values
        :param model_1_pred: a numpy array that contains values based on prediction of model 1
        :param model_2_pred: a numpy array that contains values based on prediction of model 2
        :return p_value: the probability calculated under the chi-squared distribution
        """
        mc_table = mcnemar_table(y_target=target, y_model1=model_1_pred, y_model2=model_2_pred)

        n = mc_table[0, 1] + mc_table[1, 0]
        # if the sum of b + c is less than 25, we should you use the binomial distribution
        # instead of the chi-squared distribution
        binomial = True if n < 25 else False
        _, p_value = mcnemar(ary=mc_table, exact=binomial)

        return p_value
