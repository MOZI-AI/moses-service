__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import grpc
from service_specs.moses_service_pb2 import Result
from service_specs import moses_service_pb2_grpc
from concurrent import futures
from models.dbmodels import Session
from utils.url_encoder import encode
from pymongo import MongoClient
from config import DATASET_DIR, DB_NAME, MONGODB_URI, MOZI_URI, GRPC_PORT
import uuid
import os
import time
from task.task_runner import start_analysis

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MoziService(moses_service_pb2_grpc.MosesServiceServicer):

    def __init__(self, db=None):
        if db:
            self.db = db
        else:
            self.db = MongoClient(MONGODB_URI)[DB_NAME]

    def StartAnalysis(self, request, context):

        crossval_opts = {"folds": request.crossValOpts.folds, "testSize": request.crossValOpts.testSize, "randomSeed": request.crossValOpts.randomSeed }
        moses_opts, dataset, target_feature = request.mosesOpts, request.dataset, request.target_feature

        session_id = uuid.uuid4()
        mnemonic = encode(session_id)
        cwd, file_path = self._write_dataset(dataset, session_id)

        session = Session(str(session_id), moses_opts, crossval_opts, file_path, mnemonic, target_feature)
        session.save(self.db)

        start_analysis.apply_async(args=[session, cwd])

        url = f"{MOZI_URI}/{mnemonic}"

        return Result(resultUrl=url, description="Analysis started")

    def _write_dataset(self, b_string, session_id):
        """
        Writes the dataset file and returns the directory it is saved in
        :param b_string: the base64 encoded string of the dataset file
        :param session_id: the id of the associated session
        :return: cwd: the directory where the dataset file is saved
        """
        cwd = os.path.join(DATASET_DIR, f"session_{str(session_id)}")

        if not os.path.exists(cwd):
            os.makedirs(cwd)

        file_path = os.path.join(cwd, f"{str(session_id)}.csv")

        fb = bytearray(b_string.encode(encoding="utf-8"))

        with open(file_path, "wb") as fp:
            fp.write(fb)

        return cwd, file_path


def serve(db=None):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    moses_service_pb2_grpc.add_MosesServiceServicer_to_server(MoziService(db), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    return server


if __name__ == "__main__":
    server = serve()
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
