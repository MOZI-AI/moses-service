__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from flask import Flask
from flask_restful import Api
from webserver.apiresult import ResultApi, StatusApi
from flask_cors import CORS


def setup():
    app = Flask(__name__)
    CORS(app)

    api = Api(app)
    api.add_resource(ResultApi, '/api/result/<id>')
    api.add_resource(StatusApi, '/api/status/<id>')

    return app