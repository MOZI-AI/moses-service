__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os

DATASET_DIR = os.environ["DATASETS_DIR"]

TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests/data"))

moses_options = "-j 8 --balance 1 -m 1000 -W 1 --output-cscore 1 --result-count 100 " \
                "--reduct-knob-building-effort 1 --hc-widen-search 1 --enable-fs 1 --fs-algo simple " \
                "--fs-target-size 4 --hc-crossover-min-neighbors 5000 --fs-focus all --fs-seed init " \
                "--complexity-ratio 3 --hc-fraction-of-nn .3 --hc-crossover-pop-size 1000"

crossval_options = {"folds": 3, "testSize": 0.3, "randomSeed": 3}

try:
    MONGODB_URI = os.environ["MONGODB_URI"]

except KeyError:
    MONGODB_URI = "mongodb://127.0.0.1:27017/"
try:
    REDIS_URI = os.environ["REDIS_URI"]
except KeyError:
    REDIS_URI = "redis://localhost:6379/0"

CELERY_OPTS = {'CELERY_BROKER_URL': REDIS_URI, 'CELERY_RESULT_BACKEND': REDIS_URI,
               'CELERY_TASK_SERIALIZER': 'pickle', 'CELERY_ACCEPT_CONTENT': ['pickle']}

DB_NAME = "mozi_snet"
