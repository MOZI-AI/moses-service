__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from abc import ABCMeta, abstractmethod
import math

class BaseFilter(metaclass=ABCMeta):
    """
    This is an abstract class that defines a single method filter to be implemented by subclasses
    """
    @abstractmethod
    def cut_off(self, models, value):
        pass

    def filter_negatives(self, models):
        """
        Filter out models that have a negative score
        :param models: A list of Model objects
        :return:
        """
        result = []
        for model in models:
            if any([x < 0 or math.isnan(x) for x in model.scores()]):
                continue
            result.append(model)

        return result