__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import grpc
from service_specs.moses_service_pb2 import AnalysisParameters, CrossValOptions, Filter
from service_specs.moses_service_pb2_grpc import MosesServiceStub
import base64
import sys
import yaml
from config import GRPC_HOST, GRPC_PORT


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

    filter_val = Filter(score=opts["filter"]["score"], value=opts["filter"]["value"])
    payload = AnalysisParameters(mosesOpts=opts["moses_opts"], crossValOpts=cross_val,
                                 targetFeature=opts["target_feature"], filter=filter_val,
                                 dataset=dataset)

    return stub.StartAnalysis(payload)


if __name__ == "__main__":

    if len(sys.argv) == 3:
        try:
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = MosesServiceStub(channel)
            result = run_analysis(stub, sys.argv[1], sys.argv[2])
            print(result)
        except grpc.RpcError as e:
            print(e.details())
    else:
        print(f"Usage: python {__file__} options.yaml <input_file>")
