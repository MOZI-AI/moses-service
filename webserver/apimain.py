__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import zipfile
import os
from models.dbmodels import Session
from flask import Flask, send_file, jsonify
from flask_cors import CORS
import pymongo
from config import MONGODB_URI, DB_NAME, DATASET_DIR

app = Flask(__name__)
CORS(app)


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
        if session.status == 2 or session.status == -1:
            return jsonify({"status": session.status, "progress": session.progress, "start_time": session.start_time, "end_time": session.end_time, "message": session.message}), 200

        return jsonify({"status": session.status, "progress": session.progress, "start_time": session.start_time, "message": session.message}), 200

    else:
        return jsonify({"response": "Session not found"}), 404


@app.route("/result/<mnemonic>", methods=["GET"])
def send_result(mnemonic):
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    session = Session.get_session(db, mnemonic=mnemonic)

    if session:
        if session.status == 2:
            swd = os.path.join(DATASET_DIR, f"session_{mnemonic}")
            zip_fp = zipfile.ZipFile(f"{swd}.zip", "w", zipfile.ZIP_DEFLATED)
            zip_dir(swd, zip_fp)
            zip_fp.close()

            return send_file(f"{swd}.zip", as_attachment=True), 200
        else:
            return jsonify({"response": "Session not finished"}), 401

    else:
        return jsonify({"response": "Session not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")