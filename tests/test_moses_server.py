__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
from unittest.mock import patch, MagicMock
from service_specs.moses_service_pb2_grpc import MosesServiceStub
import grpc
from config import TEST_DATA_DIR
import os
from service.moses_service_server import serve
from service.moses_service_client import run_analysis


class TestMosesServer(unittest.TestCase):
    server = None
    port = 6001

    @classmethod
    def setUpClass(cls):
        cls.server = serve(cls.port)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)

    def setUp(self):
        self.channel = grpc.insecure_channel(f"localhost:{self.port}")
        self.stub = MosesServiceStub(self.channel)

    def tearDown(self):
        pass

    @patch("service.moses_service_server.start_analysis")
    def test_run_analysis_happy_path(self, delay_func):
        delay_func().delay = MagicMock(name="delay")
        opts_file = os.path.join(TEST_DATA_DIR, "options.yaml")
        input_file = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        result = run_analysis(self.stub, opts_file, input_file)

        self.assertIsNotNone(result.resultUrl)
        self.assertTrue(delay_func.delay.called)
        print(result.resultUrl)

    @patch("service.moses_service_server.start_analysis")
    def test_run_analysis_error_path(self, delay_func):
        delay_func().delay = MagicMock(name="delay")
        opts_file = os.path.join(TEST_DATA_DIR, "options.yaml")
        input_file = os.path.join(TEST_DATA_DIR, "malformed.csv")

        with self.assertRaises(grpc.RpcError):
            run_analysis(self.stub, opts_file, input_file)
