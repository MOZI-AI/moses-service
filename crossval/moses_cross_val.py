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
import tempfile


class CrossValidation:
    """
    This class runs the cross-validation.
    """

    def __init__(self, session, db, cwd):
        """
        :param session: The session object that has the moses, cross-validation options and other metadata
        :param db: The db connection object
        :param cwd: Current working directory to save files to
        """
        self.session = session
        self.cwd = cwd
        self.db = db
        self.logger = logging.getLogger("mozi_snet")
        self.fold_files = []
        self._set_dir()

        self.total_runs = (self.session.crossval_options["folds"] * self.session.crossval_options["randomSeed"]) + 1
        self.runs = 0

        self.tree_transformer = ComboTreeTransform()

        logging.info(f"Current working dir: {os.getcwd()}")

    def _set_dir(self):
        if not os.path.exists(self.cwd):
            os.makedirs(self.cwd)

        os.chdir(self.cwd)

    def run_folds(self):
        """
        This the function that uses MosesRunner to run moses on training dataset and uses ModelEvaluator to score the
        models on the test and training data
        :return:
        """
        x, cols, cv = self.split_dataset()
        i = 0
        for train_index, test_index in cv:
            train_file, test_file = tempfile.NamedTemporaryFile().name, tempfile.NamedTemporaryFile().name

            seeds = self._generate_seeds(self.session.crossval_options["randomSeed"])
            x_train, x_test = x[train_index], x[test_index]
            pd.DataFrame(x_train, columns=cols).to_csv(train_file, index=False)
            pd.DataFrame(x_test, columns=cols).to_csv(test_file, index=False)
            files = []

            for file in self.run_seeds(seeds, i, train_file):
                files.append(file)

            fold_fname = f"fold_{i}.csv"
            self.fold_files.append(fold_fname)

            CrossValidation.merge_fold_files(fold_fname, files)
            self.logger.info("Evaluating fold: %d" % i)
            self.score_fold(fold_fname, train_file, test_file)
            self.count_features(fold_fname)

            i += 1

            self.on_progress_update()

        # save the feature count file
        models = []

        for fold in self.fold_files:
            models.extend(pd.read_csv(fold).model.values[0:5])

        ensemble_df = self.majority_vote(models)
        ensemble_df.to_csv("ensemble.csv", index=False)
        feature_count_df = pd.DataFrame.from_dict(self.tree_transformer.fcount)

        feature_count_df.to_csv("feature_count.csv")

    def split_dataset(self):
        """
        Helper method to split the dataset into train and test partitions
        :return:
        """
        df = pd.read_csv(self.session.dataset)

        x, y = df.values, df[self.session.target_feature].values
        splits, test_size = self.session.crossval_options["folds"], self.session.crossval_options["testSize"]
        cv = StratifiedShuffleSplit(n_splits=splits, test_size=test_size)

        return x, df.columns.values, cv.split(x, y)

    def run_seeds(self, seeds, i, file):
        """
        Helper method to run MOSES on a train set using random seeds
        :param seeds: The rand seed numbers
        :param i: The current fold index
        :param file: The training file
        :return: file: the output file containing the MOSES models
        """
        for seed in seeds:
            output_file = f"fold_{i}_seed_{seed}.csv"
            moses_options = " ".join([self.session.moses_options, "--random-seed " + str(seed)])

            moses_runner = MosesRunner(file, output_file, moses_options)
            returncode, stdout, stderr = moses_runner.run_moses()

            if returncode != 0:
                self.logger.error("Moses run into error: %s" % stderr.decode("utf-8"))
                raise ChildProcessError(stderr.decode("utf-8"))

            moses_runner.format_combo(output_file)
            self.runs += 1
            yield output_file

    def on_progress_update(self):
        """
        Calculates the percentage of folds that have been run and sets it as the value of the session progress attribute
        :return:
        """
        self.runs += 1

        percentage = int((self.runs / self.total_runs) * 100)

        self.session.progress = percentage

        self.session.update_session(self.db)

    def score_fold(self, fold_file, train_file, test_file):
        """
        Score the models from a fold on both test and training partitions
        :param fold_file: the model file containing the models for this fold
        :param train_file: The file containing the train set
        :param test_file: The file containing the test set
        :return:
        """
        model_evaluator = ModelEvaluator(self.session.target_feature)

        fold_df = pd.read_csv(fold_file)
        test_matrix = model_evaluator.run_eval(fold_df, test_file)
        train_matrix = model_evaluator.run_eval(fold_df, train_file)

        test_scores = model_evaluator.score_models(test_matrix, test_file)
        train_scores = model_evaluator.score_models(train_matrix, train_file)

        score_matrix = np.concatenate((test_scores, train_scores), axis=1)

        df = self.filter_scores(fold_file, score_matrix)

        df.to_csv(fold_file, index=False)

    def filter_scores(self, fold_file, scores):
        """
        Filter scores of null models and models that have NAN score values
        :param fold_file: The model file for a given fold
        :param scores: The score matrix for the models of a fold
        :return: df: a pandas dataframe that contains the models with their scores on the test and train sets
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

    def majority_vote(self, models):
        """
        Takes the top five models from each fold and does a majority voting.
         It scores the combined models on the whole dataset
        :param models: An array containing the models from each fold
        :return: ensemble_df: a Pandas dataframe containing the models with
        their individual scores and the combined score
        """
        model_df = pd.DataFrame(models, columns=["model"])
        model_eval = ModelEvaluator(self.session.target_feature)

        matrix = model_eval.run_eval(model_df, self.session.dataset)
        majority_matrix = stats.mode(matrix, nan_policy="omit").mode

        score_matrix = model_eval.score_models(matrix, self.session.dataset)
        ensemble_score = model_eval.score_models(majority_matrix, self.session.dataset)

        arr = []
        for model, score in zip(models, score_matrix):
            row = list(score)
            row.insert(0, model)
            arr.append(row)

        ensemble_score = list(ensemble_score[0])
        ensemble_score.insert(0, "ensemble")
        arr.append(ensemble_score)
        ensemble_df = pd.DataFrame(arr, columns=["model", "recall", "precision", "accuracy", "f1_score", "p_value"])

        return ensemble_df

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

        if len(dfs) > 0:
            df1.append(dfs)

        df1.to_csv(fold_file, index=False)

        for file in files:
            os.remove(file)
