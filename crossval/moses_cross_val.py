__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from models.objmodel import EnsembleModel
import os
from crossval.moses_runner import MosesRunner
from sklearn.model_selection import StratifiedShuffleSplit
import pandas as pd
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

    def __init__(self, session, db, filter_type, value, cwd):
        """
        :param session: The session object that has the moses, cross-validation options and other metadata
        :param db: The db connection object
        :param cwd: Current working directory to save files to
        """
        self.session = session
        self.cwd = cwd
        self.db = db
        self.filter = filter_type
        self.filter_value = value
        self.logger = logging.getLogger("mozi_snet")
        self.fold_files = []
        self._set_dir()

        self.total_runs = (self.session.crossval_options["folds"] * self.session.crossval_options["randomSeed"]) + 1
        self.runs = 0

        self.tree_transformer = ComboTreeTransform()
        self.result_models = {}
        self.logger.info(f"Current working dir: {os.getcwd()}")

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
        for i, (train_index, test_index) in enumerate(cv):
            train_file, test_file = tempfile.NamedTemporaryFile(mode="w+").name, tempfile.NamedTemporaryFile("w+").name

            seeds = self._generate_seeds(self.session.crossval_options["randomSeed"])
            x_train, x_test = x[train_index], x[test_index]
            pd.DataFrame(x_train, columns=cols).to_csv(train_file, index=False)
            pd.DataFrame(x_test, columns=cols).to_csv(test_file, index=False)
            fold_models = []
            for models in self.run_seeds(seeds, i, train_file):
                fold_models.extend(models)

            fold_fname = f"fold_{i}.csv"
            self.fold_files.append(fold_fname)
            self.logger.info(f"Got {len(fold_models)} for fold_{i}")
            # CrossValidation.merge_fold_files(fold_fname, files)
            self.logger.info("Evaluating fold: %d" % i)
            scored_models = self.score_fold(fold_models, train_file, test_file)
            self.count_features(scored_models)
            self.result_models[fold_fname] = scored_models
            self.write_models(fold_fname, scored_models)
            self.on_progress_update()

        ensemble_df = self.majority_vote()
        if ensemble_df is not None:
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
            output_file = tempfile.NamedTemporaryFile(mode="w+")
            moses_options = " ".join([self.session.moses_options, "--random-seed " + str(seed)])

            moses_runner = MosesRunner(file, output_file.name, moses_options)
            returncode, stdout, stderr = moses_runner.run_moses()

            if returncode != 0:
                self.logger.error("Moses run into error: %s" % stderr.decode("utf-8"))
                raise ChildProcessError(stderr.decode("utf-8"))

            self.runs += 1
            yield moses_runner.format_combo(output_file.name)

    def on_progress_update(self):
        """
        Calculates the percentage of folds that have been run and sets it as the value of the session progress attribute
        :return:
        """
        self.runs += 1

        percentage = int((self.runs / self.total_runs) * 100)

        self.session.progress = percentage

        self.session.update_session(self.db)

    def score_fold(self, models, train_file, test_file):
        """
        Score the models from a fold on both test and training partitions
        :param models: a list of model objects
        :param train_file: The file containing the train set
        :param test_file: The file containing the test set
        :return:
        """
        model_evaluator = ModelEvaluator(self.session.target_feature)

        test_matrix = model_evaluator.run_eval(models, test_file)
        train_matrix = model_evaluator.run_eval(models, train_file)

        test_scores = model_evaluator.score_models(test_matrix, test_file)
        train_scores = model_evaluator.score_models(train_matrix, train_file)

        for moses_model, score in zip(models, test_scores):
            moses_model.test_score = score

        for moses_model, score in zip(models, train_scores):
            moses_model.train_score = score

        return models

    def write_models(self, fold_name, models):
        """
        This method saves the models for a fold into a file
        :param fold_name: The file name for the file
        :param models: The list of model objects to write to file
        :return:
        """
        data = {"model": [], "complexity": [], "recall_test": [], "precision_test": [], "accuracy_test": [],
                "f1_test": [], "p_value_test": [],
                "recall_train": [], "precision_train": [], "accuracy_train": [], "f1_train": [], "p_value_train": []}

        for model in models:
            for k in data:
                data[k].append(model[k])

        df = pd.DataFrame(data)
        df.to_csv(fold_name, index=False)

    def count_features(self, models):
        """
        Count the unique features that are found in models of a fold.
        :param fold_file:
        :return:
        """

        for moses_model in models:
            tree = combo_parser.parse(moses_model.model)
            self.tree_transformer.transform(tree)

    def majority_vote(self):
        """
        Takes the top five models from each fold and does a majority voting.
         It scores the combined models on the whole dataset
        :param models: An array containing the models from each fold
        :return: ensemble_df: a Pandas dataframe containing the models with
        their individual scores and the combined score
        """
        data = {"model": [], "recall": [], "precision": [], "accuracy": [], "f1_score": [], "p_value": []}
        model_eval = ModelEvaluator(self.session.target_feature)
        filtered_models = []
        for _, v in self.result_models.items():
            res = self.filter.cut_off(v, self.filter_value)
            if len(res) > 0:
                filtered_models.extend(res)

        if len(filtered_models) == 0:
            return None
        ensemble_models = list(map(lambda k: EnsembleModel(k.model, k.test_score), filtered_models))
        matrix = model_eval.run_eval(ensemble_models, self.session.dataset)
        majority_matrix = stats.mode(matrix, nan_policy="omit").mode

        score_matrix = model_eval.score_models(matrix, self.session.dataset)
        ensemble_score = model_eval.score_models(majority_matrix, self.session.dataset)

        ensemble_model = EnsembleModel("ensemble", ensemble_score[0])
        ensemble_models.append(ensemble_model)
        score_matrix.append(ensemble_score[0])

        for model, _ in zip(ensemble_models, score_matrix):
            for k in data:
                data[k].append(model[k])

        ensemble_df = pd.DataFrame(data)

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