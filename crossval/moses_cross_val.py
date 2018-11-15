__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os

class CrossValidation:
    def __init__(self, session, db):
        self.session = session
        self.db = db


    def _set_dir(self):
        if not os.path.exists(RESULT_FOLDER):
            os.makedirs(RESULT_FOLDER)

        os.chdir(RESULT_FOLDER)
        if not os.path.exists("session_" + self.id):
            os.mkdir("session_" + self.id)

        os.chdir("session_" + self.id)

        path = str(self.session.seq_num) + '_' + str(self.session.total_runs)

        if not os.path.exists(path):
            os.mkdir(path)

        os.chdir(path)