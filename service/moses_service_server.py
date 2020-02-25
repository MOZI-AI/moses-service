__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import contextlib
import multiprocessing
import socket
import time
import uuid
from concurrent import futures

import grpc
import pandas as pd

from config import MOZI_URI, GRPC_PORT, setup_logging
from config import get_logger
from service_specs import moses_service_pb2_grpc
from service_specs.moses_service_pb2 import Result
from task.task_runner import start_analysis
from utils.url_encoder import encode

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = _PROCESS_COUNT


class MosesService(moses_service_pb2_grpc.MosesServiceServicer):

    def StartAnalysis(self, request, context):
        session_id = uuid.uuid4()
        mnemonic = encode(session_id)
        logger = get_logger(mnemonic)

        crossval_opts = {"folds": request.crossValOpts.folds, "testSize": request.crossValOpts.testSize,
                         "randomSeed": request.crossValOpts.randomSeed}
        moses_opts, dataset, target_feature = request.mosesOpts, request.dataset, request.targetFeature
        filter_opts = {"score": request.filter.score, "value": request.filter.value}
        logger.info(f"Received request with Moses Options: {moses_opts}\n Cross Validation Options: {crossval_opts}\n")

        if is_valid_dataset(dataset, target_feature):
            start_analysis.delay(id=session_id, moses_options=moses_opts, crossval_options=crossval_opts,
                                 filter_opts=filter_opts, dataset=dataset, mnemonic=mnemonic,
                                 target_feature=target_feature)

            url = f"{MOZI_URI}/?id={mnemonic}"
            logger.info(f"Session {session_id} analysis started.")
            return Result(resultUrl=url, description="Analysis started")

        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid dataset.Dataset doesn't contain a column with named {target_feature} or has "
                                f"invalid characters")
            logger.error("Error occurred while validating request")
            return Result(resultUrl="",
                          description=f"Validation error occurred. Dataset doesn't contain a column with named {target_feature} or has invalid characters")


def is_valid_dataset(dataset, target_feature):
    """
    Checks if a dataset is a valid or not
    :param b_string: The base64 encoded string of the dataset file
    :param target_feature: The target feature column name
    :return:
    """
    df = pd.read_csv(dataset)

    # check if the target_feature exists
    if not {target_feature}.issubset(df.columns):
        return False

    invalid_df = df.filter(regex="[$!()]+", axis="columns")

    valid = len(invalid_df.columns) == 0
    return valid


def serve(port=GRPC_PORT):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1)
    ])
    moses_service_pb2_grpc.add_MosesServiceServicer_to_server(MosesService(), server)
    server.add_insecure_port(f"[::]:{port}")
    return server


def _wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(None)


@contextlib.contextmanager
def _reserve_port():
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(('', int(GRPC_PORT)))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def _run_server(bind_address):
    """Start a server in a subprocess"""
    options = (("grpc.so_reuseport", 1), ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1))
    # WARNING: This example takes advantage of SO_REUSEPORT. Due to the
    # limitations of manylinux1, none of our precompiled Linux wheels currently
    # support this option. (https://github.com/grpc/grpc/issues/18210). To take
    # advantage of this feature, install from source with
    # `pip install grpcio --no-binary grpcio`.

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=_THREAD_CONCURRENCY),
        options=options
    )
    moses_service_pb2_grpc.add_MosesServiceServicer_to_server(MosesService(), server)
    server.add_insecure_port(bind_address)
    server.start()
    _wait_forever(server)


if __name__ == "__main__":
    setup_logging()
    with _reserve_port() as port:
        address = "0.0.0.0:{}".format(port)
        workers = []
        for _ in range(_PROCESS_COUNT):
            worker = multiprocessing.Process(
                target=_run_server, args=(address,)
            )
            worker.start()
            workers.append(workers)

        for worker in workers:
            worker.join()
