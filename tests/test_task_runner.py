__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
import os
import mongomock
import shutil
from config import TEST_DATA_DIR, moses_options, crossval_options
import uuid
from models.dbmodels import Session
from task.task_runner import start_analysis


class TestTaskRunner(unittest.TestCase):

    def setUp(self):
        dataset = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        session_id = str(uuid.uuid4())
        self.session = Session(session_id, moses_options, crossval_options, dataset, "abcd")
        self.cwd = os.path.join(TEST_DATA_DIR, f"session_{session_id}")

    def test_start_analysis(self):
        mock_db = mongomock.MongoClient().db

        self.session.save(mock_db)

        start_analysis(self.session, self.cwd, mock_db)

        tmp_session = Session.get_session(self.session.id, mock_db)
        self.assertEqual(tmp_session.status, 2)
        self.assertEqual(tmp_session.progress, 100)

    def test_start_analysis_error_path(self):
        mock_db = mongomock.MongoClient().db
        self.session.dataset = None
        self.session.save(mock_db)

        start_analysis(self.session, self.cwd, mock_db)

        tmp_session = Session.get_session(self.session.id, mock_db)

        self.assertEqual(tmp_session.status, -1)

    def tearDown(self):
        if os.path.exists(self.cwd):
            shutil.rmtree(self.cwd)


if __name__ == "__main__":
    unittest.main()