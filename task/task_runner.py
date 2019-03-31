__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import base64
import logging
import os
import shutil
import time
import traceback
from datetime import timedelta
import pymongo
from celery import Celery, current_app
from celery.bin import worker
from config import MONGODB_URI, CELERY_OPTS, DB_NAME, DATASET_DIR, EXPIRY_SPAN, SCAN_INTERVAL, setup_logging
from crossval.moses_cross_val import CrossValidation
from models.dbmodels import Session
from crossval.filters import loader

celery = Celery('mozi_snet', broker=CELERY_OPTS["CELERY_BROKER_URL"])
celery.conf.update(CELERY_OPTS)
setup_logging()


def write_dataset(b_string, mnemonic):
    """
    Writes the dataset file and returns the directory it is saved in
    :param b_string: the base64 encoded string of the dataset file
    :param mnemonic: the mnemonic of the associated session
    :return: cwd: the directory where the dataset file is saved
    """
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
    swd = os.path.join(DATASET_DIR, f"session_{mnemonic}")

    if not os.path.exists(swd):
        os.makedirs(swd)

    file_path = os.path.join(swd, f"dataset.csv")

    fb = base64.b64decode(b_string)

    with open(file_path, "wb") as fp:
        fp.write(fb)

    return swd, file_path


def get_expired_sessions(db, time_span):
    """
    Given a database object reference, it will return all the sessions where the difference between
    their end_time and the current time is greater than or equal to time_span
    :param db: Mongo object
    :param time_span: the time difference in seconds
    :return:
    """

    sessions = Session.get_finished_sessions(db)
    now = time.time()
    if len(sessions) > 0:
        expired_sessions = filter(lambda k: (now - k.end_time) > time_span, sessions)
        return expired_sessions

    return None


@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(SCAN_INTERVAL, scan_expired_sessions.s(EXPIRY_SPAN), name="Scan for expired sessions")


@celery.task(name="task.task_runner.start_analysis")
def start_analysis(**kwargs):
    """
    A celery task that runs the MOSES analysis
    :param session: The session object
    :param cwd: Current working directory to store the results of the analysis
    :param db: A reference to the mongo database
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")

    swd, file_path = write_dataset(kwargs["dataset"], kwargs["mnemonic"])
    session = Session(kwargs["id"], kwargs["moses_options"], kwargs["crossval_options"],
                      file_path, kwargs["mnemonic"], kwargs["target_feature"])

    session.save(db)

    session.status = 1
    session.progress = 1
    session.start_time = time.time()
    session.update_session(db)

    try:
        filter_type, value = kwargs["filter_opts"]["score"], kwargs["filter_opts"]["value"]
        filter_cls = loader.get_score_filters(filter_type)
        moses_cross_val = CrossValidation(session, db, filter_cls, value, swd)
        logger.info("Started cross-validation run")
        moses_cross_val.run_folds()
        logger.info("Cross-validation done successfully")
        session.status = 2
        session.message = "Success"
        session.progress = 100
    except Exception as e:
        session.status = -1
        session.message = e.__str__()
        logger.error(f"Task failed with {traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)}")

    finally:
        session.end_time = time.time()
        session.update_session(db)


@celery.task
def scan_expired_sessions(time_span):
    """
    Scans for sessions that are expired. The default time for a session expiry is two weeks.
    The time for expiry can be configured by changing the $EXPIRY_SPAN environment variable
    :param time_span: the time period for a session to expire
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")
    td = timedelta(days=time_span)
    logger.info("Scanning expired sessions")
    result = get_expired_sessions(db, td.total_seconds())

    if result:
        delete_expired_sessions.apply_async(result)


@celery.task
def delete_expired_sessions(sessions):
    """
    Deletes the results and datasets of sessions that have expired.
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")
    try:
        for session in sessions:
            zip_file = os.path.join(DATASET_DIR, f"session_{session.mnemonic}.zip")
            sess_dir = os.path.join(DATASET_DIR, f"session_{session.mnemonic}")

            os.remove(zip_file)
            shutil.rmtree(sess_dir)

            session.expired = True
            session.update_session(db)

        logger.info(f"Successfully deleted {len(sessions)} sessions")

    except Exception as ex:
        logger.error(f"Ran into error f{ex.__str__()}")


if __name__ == "__main__":
    app = current_app._get_current_object()
    worker = worker.worker(app=app)

    worker.run(**CELERY_OPTS)