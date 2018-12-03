__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import logging
import time
import uuid
from concurrent import futures
import grpc
from config import MOZI_URI, GRPC_PORT, setup_logging
from service_specs import moses_service_pb2_grpc
from service_specs.moses_service_pb2 import Result
from task.task_runner import start_analysis
from utils.url_encoder import encode
import sys

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MoziService(moses_service_pb2_grpc.MosesServiceServicer):

    def StartAnalysis(self, request, context):
        logger = logging.getLogger("mozi_snet")

        crossval_opts = {"folds": request.crossValOpts.folds, "testSize": request.crossValOpts.testSize, "randomSeed": request.crossValOpts.randomSeed }
        moses_opts, dataset, target_feature = request.mosesOpts, request.dataset, request.target_feature

        logger.info(f"Received request with Moses Options: {moses_opts}\n Cross Validation Options: {crossval_opts}\n")

        session_id = uuid.uuid4()
        mnemonic = encode(session_id)

        start_analysis.delay(id=session_id, moses_options=moses_opts, crossval_options=crossval_opts,
                             dataset=dataset, mnemonic=mnemonic, target_feature=target_feature)

        url = f"{MOZI_URI}/status/{mnemonic}"
        return Result(resultUrl=url, description="Analysis started")


def serve(port=GRPC_PORT):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    moses_service_pb2_grpc.add_MosesServiceServicer_to_server(MoziService(), server)
    server.add_insecure_port(f"[::]:{port}")
    return server


if __name__ == "__main__":
    setup_logging()
    if len(sys.argv) == 2:
        server = serve(sys.argv[1])
    else:
        server = serve()
    server.start()
    try:
        while True:
            time.sleep(8)
    except KeyboardInterrupt:
        server.stop(0)
