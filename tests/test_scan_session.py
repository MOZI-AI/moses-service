import os

__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from unittest.mock import patch, MagicMock
from config import DB_NAME, DATASET_DIR
import mongomock
from task.task_runner import get_expired_sessions, scan_expired_sessions, celery, delete_expired_sessions
import time


class TestScanSession(unittest.TestCase):

    def test_get_expired_session(self):
        session = {
            "id": "abcd", "moses_options": "", "crossval_options": "",
            "dataset": "", "mnemonic": "abcdr4e", "target_feature": "case",
            "status": 2, "end_time": time.time(), "progress": 100, "message": "",
            "start_time": 0, "expired": False
        }
        mock_db = mongomock.MongoClient().db
        mock_db.sessions.insert_one(session)
        time.sleep(3)  # to simulate session being run

        sessions = list(get_expired_sessions(mock_db, 3))

        self.assertEqual(len(sessions), 1)

    @patch("pymongo.MongoClient")
    @patch("task.task_runner.delete_expired_sessions")
    def test_scan_expired_sessions(self, mock_task, client):
        session = {
            "id": "abcd", "moses_options": "", "crossval_options": "",
            "dataset": "", "mnemonic": "abcdr4e", "target_feature": "case",
            "status": 2, "end_time": time.time(), "progress": 100, "message": "",
            "start_time": 0, "expired": False
        }
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        mock_db["sessions"].insert_one(session)

        mock_task().apply_async.return_value = None

        celery.conf.update(CELERY_ALWAYS_EAGER=True)
        time.sleep(3)  # to simulate session being run
        scan_expired_sessions.delay(3)

        mock_task.assert_called()

    @patch("pymongo.MongoClient")
    @patch("shutil.rmtree")
    @patch("os.remove")
    def test_delete_expired_sessions(self, remove, rmtree, client):
        session = {
            "id": "abcd", "moses_options": "", "crossval_options": "",
            "dataset": "", "mnemonic": "abcdr4e", "target_feature": "case",
            "status": 2, "end_time": time.time(), "progress": 100, "message": "",
            "start_time": 0, "expired": False
        }
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db

        mock_session = MagicMock()
        mock_session.mnemonic = session['mnemonic']
        mock_session.update.return_value = None

        celery.conf.update(CELERY_ALWAYS_EAGER=True)
        delete_expired_sessions([mock_session])

        zip_file = os.path.join(DATASET_DIR, f"session_{session['mnemonic']}.zip")
        sess_dir = os.path.join(DATASET_DIR, f"session_{session['mnemonic']}")

        remove.assert_called_with(zip_file)
        rmtree.assert_called_with(sess_dir)
