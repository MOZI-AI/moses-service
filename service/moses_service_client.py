__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import grpc
from service_specs.moses_service_pb2 import AnalysisParameters, CrossValOptions
from service_specs.moses_service_pb2_grpc import MosesServiceStub
import base64
import sys
import yaml
from config import GRPC_PORT, setup_logging
import logging

setup_logging()

logger = logging.getLogger("client_log")



def read_file(location):
    with open(location, "rb") as fp:
        content = fp.read()

    return base64.b64encode(content)


def run_analysis(stub, opts_file, file_path):
    with open(opts_file, "r") as fp:
        opts = yaml.load(fp)

    dataset = read_file(file_path)

    cross_val = CrossValOptions(folds=opts["cross_val_opts"]["folds"], testSize=opts["cross_val_opts"]["test_size"],
                                randomSeed=opts["cross_val_opts"]["random_seed"])
    payload = AnalysisParameters(mosesOpts=opts["moses_opts"], crossValOpts=cross_val, target_feature=opts["target_feature"],
                                 dataset=dataset)

    return stub.StartAnalysis(payload)


if __name__ == "__main__":

    if len(sys.argv) == 3:
        try:
            channel = grpc.insecure_channel(f"localhost:{GRPC_PORT}")
            stub = MosesServiceStub(channel)
            result = run_analysis(stub, sys.argv[1], sys.argv[2])
            logger.info(result)
        except grpc.RpcError as e:
            logger.error(e.details())
    else:
        logger.info(f"Usage: python {__file__} options.yaml <input_file>")
