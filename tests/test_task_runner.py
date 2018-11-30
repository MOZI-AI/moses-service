__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
import os
import mongomock
import shutil
from config import TEST_DATA_DIR, moses_options, crossval_options
import uuid
from models.dbmodels import Session
from task.task_runner import start_analysis
from unittest.mock import patch


class TestTaskRunner(unittest.TestCase):

    def setUp(self):
        self.dataset = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        self.session_id = str(uuid.uuid4())
        self.cwd = os.path.join(TEST_DATA_DIR, f"session_{self.session_id}")

    @patch("pymongo.MongoClient")
    @patch("task.task_runner.CrossValidation")
    def test_start_analysis(self, cross_val, client):
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        session = {
            "id": self.session_id, "moses_options": moses_options, "crossval_options": crossval_options,
            "dataset": self.dataset, "mnemonic": "abcdr4e", "target_feature": "case"
        }

        mock_db.sessions.insert_one(session)
        session["cwd"] = self.cwd
        cross_val.return_value.run_folds.return_value = "Run folds"

        start_analysis(**session)

        tmp_session = Session.get_session(mock_db, session_id=self.session_id)
        self.assertEqual(tmp_session.status, 2)
        self.assertEqual(tmp_session.progress, 100)

    @patch("pymongo.MongoClient")
    @patch("task.task_runner.CrossValidation")
    def test_start_analysis_error_path(self, cross_val, client):
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        session = {
            "id": self.session_id, "moses_options": moses_options, "crossval_options": crossval_options,
            "dataset": self.dataset, "mnemonic": "abcdr4e", "target_feature": "case"
        }

        mock_db.sessions.insert_one(session)
        session["cwd"] = self.cwd
        cross_val.side_effect = Exception("Mock exception")

        start_analysis(**session)

        tmp_session = Session.get_session(mock_db, session_id=self.session_id)

        self.assertEqual(tmp_session.status, -1)

    def tearDown(self):
        if os.path.exists(self.cwd):
            shutil.rmtree(self.cwd)


if __name__ == "__main__":
    unittest.main()
