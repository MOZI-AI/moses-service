__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from crossval.filters import loader, base_filter, score_filters
from models.objmodel import MosesModel, Score


class TestScoreFilter(unittest.TestCase):

    def test_loader(self):
        filter_cls = loader.get_score_filters("precision")

        self.assertTrue(isinstance(filter_cls, score_filters.PrecisionFilter))

    def test_filter_accuracy(self):
        models = []
        model_1 = MosesModel("and($ARDK, $AKFR)", 2)
        model_1.test_score = Score(0.8, 0.3, 0.1, 0.4, 0.2)
        model_1.train_score = Score(0.8, 0.3, 0.1, 0.4, 0.2)
        models.append(model_1)
        model_2 = MosesModel("or($RIPS, $RFS)", 3)
        model_2.test_score = Score(0.5, 0.3, 0.1, 0.4, 0.2)
        model_2.train_score = Score(0.5, 0.3, 0.1, 0.4, 0.2)
        models.append(model_2)
        model_3 = MosesModel("and($ARDK, $AKFR)", 2)
        model_3.test_score = Score(0.4, 0.3, -1, 0.4, 0.2)
        model_3.train_score = Score(0.4, 0.3, -1, 0.4, 0.2)
        models.append(model_3)

        acc_filter = loader.get_score_filters("recall")

        result = acc_filter.cut_off(models, 0.6)

        self.assertEqual(len(result), 1)

    def test_filter_null(self):
        models = []
        model_1 = MosesModel("and($ARDK, $AKFR)", 2)
        model_1.test_score = Score(0.8, 0.3, 0.1, 0.4, 0.2)
        model_1.train_score = Score(0.8, 0.3, 0.1, 0.4, 0.2)
        models.append(model_1)
        model_2 = MosesModel("or($RIPS, $RFS)", 3)
        model_2.test_score = Score(0.5, 0.3, 0.1, 0.4, 0.2)
        model_2.train_score = Score(0.5, 0.3, -1, 0.4, 0.2)
        models.append(model_2)

        null_filter = loader.get_score_filters("null")

        result = null_filter.cut_off(models, 0)

        self.assertEqual(len(result), 1)