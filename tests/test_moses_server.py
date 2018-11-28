__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from unittest.mock import patch, MagicMock
from service_specs.moses_service_pb2_grpc import MosesServiceStub
import grpc
from config import TEST_DATA_DIR, GRPC_PORT
import os
import mongomock
from service.moses_service_server import serve
from service.moses_service_client import run_analysis


class TestMosesServer(unittest.TestCase):
    server = None
    db = None

    @classmethod
    def setUpClass(cls):
        cls.db = mongomock.MongoClient().db
        cls.server = serve(cls.db)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)

    def setUp(self):
        self.channel = grpc.insecure_channel(f"localhost:{GRPC_PORT}")
        self.stub = MosesServiceStub(self.channel)

    def tearDown(self):
        pass

    @patch("service.moses_service_server.start_analysis")
    def test_run_analysis(self, some_func):
        some_func.appy_async = None
        some_func.return_value = 0
        opts_file = os.path.join(TEST_DATA_DIR, "options.yaml")
        input_file = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        result = run_analysis(self.stub, opts_file, input_file)

        self.assertIsNotNone(result.resultUrl)
        print(result.resultUrl)
