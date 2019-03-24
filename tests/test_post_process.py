__author__ = 'Abdulrahman Semrie<hsamireh@gmail.com>'

import unittest
import mongomock
import os
from config import TEST_DATA_DIR
from unittest.mock import patch
from crossval.post_process import PostProcess


class TestPostProcess(unittest.TestCase):

    def setUp(self):
        self.mnemonic = "folds"
        self.fold_dir = os.path.join(TEST_DATA_DIR, "folds")

    @patch("pymongo.MongoClient")
    def test_retrieve_folds(self, client):
        mock_db = mongomock.MongoClient().db

        post_process = PostProcess("accuracy", 0.2, self.mnemonic)

        post_process.db = mock_db

        post_process._retrieve_folds(TEST_DATA_DIR)

        self.assertIsNotNone(post_process.data_frame)

    @patch("pymongo.MongoClient")
    def test_fold_to_models(self, client):
        mock_db = mongomock.MongoClient().db
        post_process = PostProcess("accuracy", 0.2, self.mnemonic)
        post_process.db = mock_db

        post_process._retrieve_folds(TEST_DATA_DIR)

        post_process._folds_to_models()

        self.assertGreater(len(post_process.models), 0)

    @patch("pymongo.MongoClient")
    def test_filter_models(self, client):
        mock_db = mongomock.MongoClient().db
        post_process = PostProcess("accuracy", 0.2, self.mnemonic)
        post_process.db = mock_db

        result_models = post_process.filter_models(TEST_DATA_DIR)

        self.assertGreater(len(result_models), 0)
