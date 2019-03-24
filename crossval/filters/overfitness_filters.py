__author__ = 'Abdulrahman Semrie<hsamireh@gmail.com>'

from crossval.filters.base_filter import BaseFilter


class AccuracyFilter(BaseFilter):

    def cut_off(self, models, value):
        return list(filter(lambda k : k.train_score.accuracy - k.test_score.accuracy <= value, models))


class PrecisionFilter(BaseFilter):

    def cut_off(self, models, value):
        return list(filter(lambda k : k.train_score.precision - k.test_score.precision <= value, models))


class RecallFilter(BaseFilter):

    def cut_off(self, models, value):
        return list(filter(lambda k : k.train_score.recall - k.test_score.recall <= value, models))


class F1Score(BaseFilter):

    def cut_off(self, models, value):
        return list(filter(lambda k : k.train_score.f1_score - k.test_score.f1_score <= value, models))


class PValue(BaseFilter):

    def cut_off(self, models, value):
        return list(filter(lambda k : k.train_score.p_value - k.test_score.p_value <= value, models))