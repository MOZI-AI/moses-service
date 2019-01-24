__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from crossval.filters.base_filter import BaseFilter


class AccuracyFilter(BaseFilter):

    def cut_off(self, models, value):
        models = super().filter_negatives(models)

        return list(filter(lambda k: k.test_score.accuracy >= value, models))


class PrecisionFilter(BaseFilter):
    def cut_off(self, models, value):
        models = super().filter_negatives(models)

        return list(filter(lambda k: k.test_score.precision >= value, models))


class RecallFilter(BaseFilter):
    def cut_off(self, models, value):
        models = super().filter_negatives(models)

        return list(filter(lambda k: k.test_score.recall >= value, models))


class F1ScoreFilter(BaseFilter):
    def cut_off(self, models, value):
        models = super().filter_negatives(models)

        return list(filter(lambda k: k.test_score.f1_score >= value, models))


class PValueFilter(BaseFilter):
    def cut_off(self, models, value):
        models = super().filter_negatives(models)

        return list(filter(lambda k: k.test_score.p_value >= value, models))


class NullFilter(BaseFilter):
    def cut_off(self, models, value):
        return super().filter_negatives(models)


