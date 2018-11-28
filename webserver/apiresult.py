__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import flask
from flask_restful import Resource
from models.dbmodels import Session
from config import DATASET_DIR
import shutil
import os
import pymongo
from config import MONGODB_URI, DB_NAME


class StatusApi(Resource):

    def __init__(self):
        self.db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
        super(StatusApi, self).__init__()

    def get(self, id):

        session = Session.get_session_mnemonic(id, self.db)

        if session:
            return {"status": session.status, "progress": session.progress, "start_time": session.start_time}, 200

        else:
            return "Session not found", 404


class ResultApi(Resource):
    def __init__(self):
        self.db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
        super(ResultApi, self).__init__()

    def get(self, id):

        session = Session.get_session_mnemonic(id, self.db)

        if session.status == 2:
            swd = os.path.join(DATASET_DIR, f"session_{session.id}")
            archive_name = os.path.join(DATASET_DIR, f"session_{session.id}/result")
            shutil.make_archive(archive_name, "zip", swd)

            return flask.send_from_directory(swd, f"{archive_name}.zip", as_attachment=True), 200

        else:
            return "Session not finished", 401