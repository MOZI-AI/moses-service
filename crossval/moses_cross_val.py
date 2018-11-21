__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os
from crossval.moses_runner import MosesRunner
from sklearn.model_selection import StratifiedShuffleSplit
import pandas as pd
import numpy as np
import random
import logging
from crossval.model_evaluator import ModelEvaluator
import math
from utils.feature_count import combo_parser, ComboTreeTransform
from scipy import stats

class CrossValidation:
    """
    This class runs the cross-validation. It depends on MosesRunner and ModelEvaluator
    """

    def __init__(self, session, db, cwd):
        """
        :param session: The session object that has the moses, cross-validation options and other metadata
        :param db: A reference to the db connection object
        :param cwd: Current working directory to save files to
        """
        self.session = session
        self.db = db
        self.cwd = cwd
        self.logger = logging.getLogger("mozi_snet")

        self.train_file, self.test_file = None, None
        self.fold_files = []
        self._set_dir()

        self.tree_transformer = ComboTreeTransform()

    def _set_dir(self):
        if not os.path.exists(self.cwd):
            os.makedirs(self.cwd)

        os.chdir(self.cwd)

    def run_folds(self):
        """
        This the function that uses MosesRunner to run moses on training dataset and uses ModelEvaluator to score the models on the test and training data
        :return:
        """
        df = pd.read_csv(self.session.dataset)

        X, y = df.values, df[self.session.target_feature].values
        splits, test_size = self.session.crossval_options["folds"], self.session.crossval_options["testSize"]
        cv = StratifiedShuffleSplit(n_splits=splits, test_size=test_size)

        self.train_file, self.test_file = "train_file", "test_file"

        i = 0
        for train_index, test_index in cv.split(X, y):
            seeds = self._generate_seeds(self.session.crossval_options["randomSeed"])

            x_train, x_test = X[train_index], X[test_index]

            pd.DataFrame(x_train, columns=df.columns.values).to_csv(self.train_file, index=False)

            pd.DataFrame(x_test, columns=df.columns.values).to_csv(self.test_file, index=False)

            files = []

            fold_fname = "fold_%d.csv" % i
            self.fold_files.append(fold_fname)

            for seed in seeds:
                output_file = "fold_{0}_seed_{1}.csv".format(str(i), str(seed))
                files.append(output_file)
                moses_options = " ".join([self.session.moses_options, "--random-seed " + str(seed)])

                moses_runner = MosesRunner(self.train_file, output_file, moses_options)
                returncode, stdout, stderr = moses_runner.run_moses()

                if returncode != 0:
                    self.logger.error("Moses run into error: %s" % stderr.decode("utf-8"))
                    raise ChildProcessError("Moses run into error: %s" % stderr.decode("utf-8"))

                moses_runner.format_combo(output_file)

            CrossValidation.merge_fold_files(fold_fname, files)
            self.logger.info("Evaluating fold: %d" % i)
            self.score_fold(i, fold_fname)
            self.count_features(fold_fname)

            i += 1

        # save the feature count file

        feature_count_df = pd.DataFrame.from_dict(self.tree_transformer.fcount)

        feature_count_df.to_csv("feature_count.csv")

    def score_fold(self, fold, fold_fname):
        model_evaluator = ModelEvaluator(self.session.target_feature)

        test_matrix = model_evaluator.run_eval(fold_fname, self.test_file)
        train_matrix = model_evaluator.run_eval(fold_fname, self.train_file)

        test_scores = model_evaluator.score_models(test_matrix, self.test_file)
        train_scores = model_evaluator.score_models(train_matrix, self.train_file)

        score_matrix = np.concatenate((test_scores, train_scores), axis=1)

        df = self.filter_scores(fold_fname, score_matrix)

        ensemble_scores = self.majority_vote(test_matrix)

        top_models = df["model"].values[0:5]

        arr = []

        for model in top_models:
            row = [model]
            row.extend(ensemble_scores[0])
            arr.append(row)

        ensemble_df = pd.DataFrame(arr, columns=["model", "recall", "precision", "accuracy", "f1_score", "p_value"])

        df.to_csv(fold_fname, index=False)
        ensemble_df.to_csv("ensemble_%d.csv" % fold, index=False)



    def filter_scores(self, fold_file, scores):
        """
        Filter scores of null models and models that have NAN score values
        :param fold_file: The model file for a given fold
        :param scores: The score matrix for the models of a fold
        :return:
        """
        labels = ["recall_test ", "precision_test", "accuracy_test", "f1_test", "p_value_test",
                 "recall_train", "precision_train", "accuracy_train", "f1_train", "p_value_train"]

        df = pd.read_csv(fold_file)

        for i, row in enumerate(scores):
            if any(score < 0 or math.isnan(score) for score in scores[i]):
                df.drop(df.index[[i]])
            else:
                 for label, score in zip(labels, row):
                    df.loc[i, label] = score

        return df

    def count_features(self, fold_file):
        """
        Count the unique features that are found in models of a fold.
        :param fold_file:
        :return:
        """
        df = pd.read_csv(fold_file)

        models = df["model"].values

        for model in models:
            tree = combo_parser.parse(model)
            self.tree_transformer.transform(tree)

    def majority_vote(self, matrix):
        top_matrix = matrix[0:5]

        majority_scores = stats.mode(top_matrix, nan_policy="omit").mode

        model_evaluator = ModelEvaluator(self.session.target_feature)

        scores = model_evaluator.score_models(majority_scores, self.test_file)

        return scores


    @staticmethod
    def _generate_seeds(num_seeds, num_pop=10000):
        """
        This functions returns an array of random numbers sampled from a population of size num_pop
        :param num_seeds: The size of the array i.e, the number of random seeds to generate
        :param num_pop: Sample size
        :return:
        """
        return random.sample(range(1, num_pop), num_seeds)

    @staticmethod
    def merge_fold_files(fold_file, files):
        """
        Merges each model file for each seed into one
        :param fold_file: The fold file to merge all the models
        :param files: An array that contains file names for each seed
        :return:
        """
        df1 = pd.read_csv(files[0])

        dfs = []
        for file in files[1:]:
            dfs.append(pd.read_csv(file))

        df1.append(dfs)

        df1.to_csv(fold_file, index=False)

        for file in files: os.remove(file)