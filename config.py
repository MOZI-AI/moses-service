__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os

DATASET_DIR = os.environ["DATASETS_DIR"]

TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests/data"))

moses_options = "-j 8 --balance 1 -m 1000 -W 1 --output-cscore 1 --result-count 100 " \
                          "--reduct-knob-building-effort 1 --hc-widen-search 1 --enable-fs 1 --fs-algo simple " \
                          "--fs-target-size 4 --hc-crossover-min-neighbors 5000 --fs-focus all --fs-seed init " \
                          "--complexity-ratio 3 --hc-fraction-of-nn .3 --hc-crossover-pop-size 1000"

crossval_options = {"folds": 3, "testSize": 0.3, "randomSeed": 3}
