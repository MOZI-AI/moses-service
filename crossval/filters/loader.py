__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import importlib
import inspect
from crossval.filters.base_filter import BaseFilter
import logging

logger = logging.getLogger("mozi_snet")


def get_score_filters(filter_name):
    try:
        filter_name = filter_name.lower().replace("-", "").replace("_", "")
        module = importlib.import_module(".score_filters", "crossval.filters")
        classes = inspect.getmembers(module, lambda k: inspect.isclass(k))

        for name, _class in classes:
            if issubclass(_class, BaseFilter) and name.lower().find(filter_name.lower()) != -1:
                logger.info(f"Using {filter_name} score for filtering")
                return _class()

    except ImportError:
        logger.error(f"Couldn't find a filter class for {filter_name}")
        return None


def get_overfitness_filter(filter_name):
    try:
        module = importlib.import_module(".overfitness_filters", "crossval.filters")
        classes = inspect.getmembers(module, lambda k: inspect.isclass(k))

        for name, _class in classes:
            if issubclass(_class, BaseFilter) and name.lower().find(filter_name) != -1:
                return _class()

    except ImportError:
        return None