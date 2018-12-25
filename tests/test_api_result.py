__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from unittest.mock import patch, MagicMock
import mongomock
from webserver.apimain import app
from models.dbmodels import Session
from flask import jsonify


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        pass

    @patch("pymongo.MongoClient")
    def test_status(self, client):
        temp_session = Session("abcd", "", "", "", "5abcd")
        temp_session.status = 1
        temp_session.progress = 40

        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db

        temp_session.save(mock_db)

        response = self.app.get("/status/5abcd")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["progress"], 40)
        self.assertEqual(response.json["status"], 1)

    @patch("pymongo.MongoClient")
    def test_status_error(self, client):

        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        mock_db.find_one.return_value = None

        resonse = self.app.get("/status/5abcd")

        self.assertEqual(resonse.status_code, 404)

    @patch("webserver.apimain.send_file")
    @patch("webserver.apimain.zip_dir")
    @patch("pymongo.MongoClient")
    def test_result_api(self, client, make_archive, send_file):
        temp_session = Session("abcd", "", "", "", "5abcd")
        temp_session.status = 2
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        temp_session.save(mock_db)

        make_archive.return_value = "Test mock"
        with app.test_request_context():
            send_file.return_value = jsonify({"response": "File sent"})

        response = self.app.get("/result/5abcd")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(make_archive.called)
        self.assertTrue(send_file.called)

    @patch("pymongo.MongoClient")
    def test_result_api_expired(self, client):
        temp_session = Session("abcd", "", "", "", "5abcd")
        temp_session.expired = True
        temp_session.status = 2
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        temp_session.save(mock_db)

        response = self.app.get("/result/5abcd")
        self.assertEqual(response.status_code, 400)