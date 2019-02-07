__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import logging
import time
import uuid
from concurrent import futures
import grpc
from config import MOZI_URI, GRPC_PORT, setup_logging, DATASET_DIR
from service_specs import moses_service_pb2_grpc
from service_specs.moses_service_pb2 import Result
from task.task_runner import start_analysis
from utils.url_encoder import encode
import sys
import os
import base64
import pandas as pd
import tempfile

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MosesService(moses_service_pb2_grpc.MosesServiceServicer):

    def StartAnalysis(self, request, context):
        logger = logging.getLogger("mozi_snet")

        crossval_opts = {"folds": request.crossValOpts.folds, "testSize": request.crossValOpts.testSize, "randomSeed": request.crossValOpts.randomSeed}
        moses_opts, dataset, target_feature = request.mosesOpts, request.dataset, request.targetFeature
        filter_opts = {"score": request.filter.score, "value": request.filter.value}
        logger.info(f"Received request with Moses Options: {moses_opts}\n Cross Validation Options: {crossval_opts}\n")

        session_id = uuid.uuid4()
        mnemonic = encode(session_id)

        if is_valid_dataset(dataset, target_feature):
            start_analysis.delay(id=session_id, moses_options=moses_opts, crossval_options=crossval_opts,
                                 filter_opts=filter_opts, dataset=dataset, mnemonic=mnemonic,
                                 target_feature=target_feature)

            url = f"{MOZI_URI}/?id={mnemonic}"
            return Result(resultUrl=url, description="Analysis started")

        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid dataset.Dataset doesn't contain a column with named {target_feature} or has "
                                f"invalid characters")

            return Result(resultUrl="Validation error occurred", description=f"Dataset doesn't contain a column with named {target_feature} or has invalid characters")


def is_valid_dataset(b_string, target_feature):
    """
    Checks if a dataset is a valid or not
    :param b_string: The base64 encoded string of the dataset file
    :param target_feature: The target feature column name
    :return:
    """

    fd, file_path = tempfile.mkstemp()

    fb = base64.b64decode(b_string)

    with open(fd, "wb") as fp:
        fp.write(fb)

    df = pd.read_csv(file_path)

    # check if the target_feature exists
    if not {target_feature}.issubset(df.columns):
        return False

    invalid_df = df.filter(regex="[$!()]+", axis="columns")

    valid = len(invalid_df.columns) == 0
    os.remove(file_path)
    return valid


def serve(port=GRPC_PORT):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
          ('grpc.max_send_message_length', -1),
          ('grpc.max_receive_message_length', -1)
    ])
    moses_service_pb2_grpc.add_MosesServiceServicer_to_server(MosesService(), server)
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
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
