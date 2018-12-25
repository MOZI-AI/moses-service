__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os
import logging
import logging.config
import yaml


DATASET_DIR = os.environ["DATASETS_DIR"]

TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests/data"))

moses_options = "-j 8 --balance 1 -m 1000 -W 1 --output-cscore 1 --result-count 100 " \
                "--reduct-knob-building-effort 1 --hc-widen-search 1 --enable-fs 1 --fs-algo simple " \
                "--fs-target-size 4 --hc-crossover-min-neighbors 5000 --fs-focus all --fs-seed init " \
                "--complexity-ratio 3 --hc-fraction-of-nn .3 --hc-crossover-pop-size 1000"

crossval_options = {"folds": 3, "testSize": 0.3, "randomSeed": 3}


MONGODB_URI = os.environ["MONGODB_URI"]
REDIS_URI = os.environ["REDIS_URI"]

EXPIRY_SPAN = float(os.environ["EXPIRY_SPAN"]) # the expiration period for a session in seconds
SCAN_INTERVAL = 3600 * 24  # every 24hrs

CELERY_OPTS = {'CELERY_BROKER_URL': REDIS_URI, 'CELERY_RESULT_BACKEND': REDIS_URI}

DB_NAME = "mozi_snet"

MOZI_URI = "http://localhost"

GRPC_PORT = "5003"


def setup_logging(default_path='logging.yml', default_level=logging.INFO):
    """Setup logging configuration
    """
    if os.path.exists(default_path):
        with open(default_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
