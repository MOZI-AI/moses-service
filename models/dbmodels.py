__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import os


class Session:
    """
    A class that represents a single run of the MOSES analysis
    """

    def __init__(self, id, moses_options, crossval_options, dataset, mnemonic, target_feature="case"):
        self.id = id
        self.moses_options = moses_options
        self.crossval_options = crossval_options
        self.dataset = dataset
        self.status = 0
        self.progress = 0
        self.message = ""
        self.start_time = 0
        self.end_time = 0
        self.target_feature = target_feature
        self.mnemonic = mnemonic
        self.expired = False

    def save(self, db):
        """
        Save the session into a database
        :param db: The database to insert the session into
        :return:
        """
        data = self.__dict__
        db["sessions"].insert_one(data)

    def delete_session(self, db):
        db["sessions"].delete_one({"id": self.id})

        # deleting a session also means deleting its dataset
        if os.path.exists(self.dataset):
            os.remove(self.dataset)

    def update_session(self, db):
        data = self.__dict__
        db["sessions"].update_one({
            "id": self.id
        }, {
            "$set": data
        })

    @staticmethod
    def get_session(db, session_id=None, mnemonic=None):
        """
        Get a session using its id or mnemonic from a database
        :param db: the db in which the session is found
        :param session_id: the id of the session
        :param mnemonic: the mnemonic value for the session derived from its uuid
        :return: A session object
        """
        result = None
        if session_id:
            result = db["sessions"].find_one({
                "id": session_id
            })

        elif mnemonic:
            result = db["sessions"].find_one({
                "mnemonic": mnemonic
            })

        if result:
            session = Session(result["id"], result["moses_options"], result["crossval_options"], result["dataset"], result["mnemonic"] ,result["target_feature"])
            session.status = result["status"]
            session.message = result["message"]
            session.start_time = result["start_time"]
            session.end_time = result["end_time"]
            session.progress = result["progress"]
            session.expired = result["expired"]

            return session

        return result

    @staticmethod
    def get_finished_sessions(db):
        """
        Find sessions that have finished, both that ran into an error or successfully finished
        :param db:
        :return:
        """

        sessions = db["sessions"].find({
            "$and": [{"status": {"$ne": 0}}, {"status": {"$ne": 1}}, {"expired": {"$ne": True}}]
        })

        result = []

        for s in sessions:
            session = Session(s["id"], s["moses_options"], s["crossval_options"], s["dataset"],
                              s["mnemonic"], s["target_feature"])
            session.status = s["status"]
            session.message = s["message"]
            session.start_time = s["start_time"]
            session.end_time = s["end_time"]
            session.progress = s["progress"]
            session.expired = s["expired"]

            result.append(session)

        return result


