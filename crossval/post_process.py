__author__ = 'Abdulrahman Semrie<hsamireh@gmail.com>'

import pymongo
from config import MONGODB_URI, DB_NAME, DATASET_DIR
import os
import pathlib
import pandas as pd
from crossval.filters import loader
from models.objmodel import Score, MosesModel


class PostProcess:

    def __init__(self, filter_type, filter_value, mnemonic):
        self.filter_type = filter_type
        self.filter_value = filter_value
        self.mnemonic = mnemonic

        self.data_frame = None

        self.session = None
        self.models = []

    def _retrieve_folds(self, base_dir):
        swd = os.path.join(base_dir,  f"session_{self.mnemonic}")
        assert os.path.exists(swd)
        path = pathlib.Path(swd)

        for fold_file in path.glob("fold_[0-9].csv"):
            if self.data_frame is None:
                self.data_frame = pd.read_csv(str(fold_file.absolute()))

            else:
                self.data_frame = self.data_frame.append(pd.read_csv(str(fold_file.absolute())))

    def _folds_to_models(self):
        for i, row in self.data_frame.iterrows():
            model = MosesModel(row["model"], row['complexity'])
            model.test_score = Score(row["recall_test"], row["precision_test"], row["accuracy_test"], row["f1_test"], row["p_value_test"])
            model.train_score = Score(row["recall_train"], row["precision_train"], row["accuracy_train"], row["f1_train"], row["p_value_train"])
            self.models.append(model)

    def filter_models(self, base_dir=DATASET_DIR):
        self._retrieve_folds(base_dir)
        self._folds_to_models()

        filtered_models = []
        filter_cls = loader.get_overfitness_filter(self.filter_type)

        if filter_cls is not None:
            filtered_models = filter_cls.filter_negatives(self.models)
            filtered_models = filter_cls.cut_off(filtered_models, self.filter_value)

        return list(map(lambda m: m.__dict__(), filtered_models))