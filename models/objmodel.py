__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'
import math
from abc import  ABCMeta, abstractmethod

class BaseModel(metaclass=ABCMeta):
    def __init__(self, model, complexity):
        self.__model = model
        self.__complexity = complexity

    @property
    def model(self):
        return self.__model

    @property
    def complexity(self):
        return self.__complexity

    @abstractmethod
    def scores(self):
        pass


class EnsembleModel(BaseModel):
    def __init__(self, model, score):
        super().__init__(model, "")
        self.score = score

    def __dict__(self):
        return {"model": self.model, "recall": self.score.recall, "precision": self.score.precision, "accuracy": self.score.accuracy, "f1_score": self.score.f1_score, "p_value":
                self.score.p_value}

    def __getitem__(self, item):
        return self.__dict__()[item]

    def scores(self):
        return [self.score.recall, self.score.precision, self.score.accuracy, self.score.f1_score,
                self.score.p_value]


class MosesModel(BaseModel):
    def __init__(self, model, complexity):
        super(MosesModel, self).__init__(model, complexity)
        self.train_score = None
        self.test_score = None

    def __dict__(self):
        return {"model": self.model, "complexity": self.complexity, "recall_test": self.test_score.recall,
                "precision_test": self.test_score.precision,
                "accuracy_test": self.test_score.accuracy, "f1_test": self.test_score.f1_score,
                "p_value_test": self.test_score.p_value, "recall_train": self.train_score.recall, "precision_train":
                    self.train_score.precision, "accuracy_train": self.train_score.accuracy,
                "f1_train": self.train_score.f1_score, "p_value_train":
                    self.train_score.p_value}

    def scores(self):
        return [self.test_score.recall, self.test_score.precision, self.test_score.accuracy, self.test_score.f1_score,
                self.test_score.p_value, self.train_score.recall, self.train_score.precision, self.train_score.accuracy,
                self.train_score.f1_score, self.train_score.p_value]

    def __getitem__(self, item):
        return self.__dict__()[item]


class Score:
    def __init__(self, recall, precision, accuracy, f1_score, p_value):
        self.__recall = recall
        self.__precision = precision
        self.__accuracy = accuracy
        self.__f1_score = f1_score
        self.__p_value = p_value

    @property
    def accuracy(self):
        return self.__accuracy

    @accuracy.setter
    def accuracy(self, value):
        if math.isnan(value):
            self.__accuracy = -1
        else:
            self.__accuracy = value

    @property
    def recall(self):
        return self.__recall

    @recall.setter
    def recall(self, value):
        if math.isnan(value):
            self.__recall = -1
        else:
            self.__recall = value

    @property
    def precision(self):
        return self.__precision

    @precision.setter
    def precision(self, value):
        if math.isnan(value):
            self.__precision = -1
        else:
            self.__precision = value

    @property
    def f1_score(self):
        return self.__f1_score

    @f1_score.setter
    def f1_score(self, value):
        if math.isnan(value):
            self.__f1_score = -1
        else:
            self.__f1_score = value

    @property
    def p_value(self):
        return self.__p_value

    @p_value.setter
    def p_value(self, value):
        if math.isnan(value):
            self.__p_value = -1
        else:
            self.__p_value = value
