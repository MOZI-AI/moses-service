__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import zipfile
import os
from models.dbmodels import Session
from flask import Flask, send_file, jsonify, request, after_this_request
from flask_cors import CORS
import pymongo
from config import MONGODB_URI, DB_NAME, DATASET_DIR, EXPIRY_SPAN
from datetime import timedelta
import jsonpickle
import redis
import pandas as pd
import tempfile as tmp
import time
from crossval.post_process import PostProcess
import logging


app = Flask(__name__)
CORS(app)

logger = logging.getLogger("mozi_snet")

def zip_dir(path, zp):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                zp.write(file_path, arcname=file)


@app.route("/status/<mnemonic>", methods=["GET"])
def check_status(mnemonic):
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]

    session = Session.get_session(db, mnemonic=mnemonic)

    if session:
        if session.status == 1:
            return jsonify({"status": session.status, "progress": session.progress, "start_time": session.start_time, "end_time": session.end_time, "message": session.message}), 200

        elif session.status == 2 or session.status == -1:
            td = timedelta(days=EXPIRY_SPAN)
            time_to_expire = td.total_seconds() - (time.time() - session.end_time)
            return jsonify({"status": session.status, "progress": session.progress, "start_time": session.start_time, "message": session.message, "end_time": session.end_time, "expire_time": time_to_expire}), 200

    else:
        return jsonify({"response": "Session not found"}), 404


@app.route("/result/<mnemonic>", methods=["GET"])
def send_result(mnemonic):
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    session = Session.get_session(db, mnemonic=mnemonic)

    if session:
        if session.status == 2 and not session.expired:
            swd = os.path.join(DATASET_DIR, f"session_{mnemonic}")
            zip_fp = zipfile.ZipFile(f"{swd}.zip", "w", zipfile.ZIP_DEFLATED)
            zip_dir(swd, zip_fp)
            zip_fp.close()

            return send_file(f"{swd}.zip", as_attachment=True), 200
        elif session.expired:
            return jsonify({"response": "Session has expired."}), 400
        elif session.status != 2:
            return jsonify({"response", "Session not finished"}), 401

    else:
        return jsonify({"response": "Session not found"}), 404


@app.route("/filter/<mnemonic>", methods=["GET"])
def filter_models(mnemonic):
    filter_type = request.args.get("filter")
    filter_value = request.args.get("value")

    if filter_type is None or filter_value is None:
        return jsonify({"message":"Filter type and value required"}), 400

    try:
        value = float(filter_value)
        assert 0 < value < 1
    except Exception:
        return jsonify({"message": "Filter value must be a float between 0 and 1"}), 400
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    session = Session.get_session(db, mnemonic=mnemonic)

    if session is None:
        return jsonify({"message": "Session not found"}), 404

    client = redis.Redis(host="redis")
    if client.exists(mnemonic) > 0:
        client.delete(mnemonic)

    post_process_filter = PostProcess(filter_type, value, mnemonic)
    try:
        models = post_process_filter.filter_models()
    except AssertionError:
        return jsonify({"message": "Session File not found"}), 404

    json_dump = jsonpickle.encode(models, unpicklable=False)
    client.set(mnemonic, json_dump, ex=600)
    return jsonify({"models": json_dump}), 200


@app.route("/filter/<mnemonic>/download", methods=["GET"])
def download_filter(mnemonic):
    client = redis.Redis(host="redis")
    if client.exists(mnemonic) == 0:
        return jsonify({"message": "Try to filter again"}), 400
    values = client.get(mnemonic).decode("utf-8")

    models = jsonpickle.decode(values)

    df = pd.DataFrame.from_dict(models)
    col_order = [5, 2, 0, 6, 8, 10, 3, 1, 7, 9, 11]
    df = df[df.columns[col_order]]
    file_path = tmp.NamedTemporaryFile(suffix=".csv", delete=True)
    df.to_csv(file_path.name, index=False)

    @after_this_request
    def remove_file(response):
        try:
            file_path.close()
            client.delete(mnemonic) # delete the key & its value from redis
        except Exception as error:
            logger.error(f"Error removing or closing downloaded file handle: {str(error)}")
        return response

    return send_file(file_path.name, as_attachment=True, mimetype="text/csv", attachment_filename=f"{mnemonic}_filter.csv"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")