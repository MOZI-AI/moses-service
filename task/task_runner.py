__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from celery import Celery
import traceback
import logging
import pymongo
from config import MONGODB_URI, CELERY_OPTS, DB_NAME, DATASET_DIR, setup_logging
import time
from crossval.moses_cross_val import CrossValidation
from models.dbmodels import Session
import os
import base64


celery = Celery('mozi_snet', broker=CELERY_OPTS["CELERY_BROKER_URL"])
celery.conf.update(CELERY_OPTS)


def write_dataset(b_string, mnemonic):
    """
    Writes the dataset file and returns the directory it is saved in
    :param b_string: the base64 encoded string of the dataset file
    :param mnemonic: the mnemonic of the associated session
    :return: cwd: the directory where the dataset file is saved
    """
    swd = os.path.join(DATASET_DIR, f"session_{mnemonic}")

    if not os.path.exists(swd):
        os.makedirs(swd)

    file_path = os.path.join(swd, f"dataset.csv")

    fb = base64.b64decode(b_string)

    with open(file_path, "wb") as fp:
        fp.write(fb)

    return swd, file_path

@celery.task
def start_analysis(**kwargs):
    """
    A celery task that runs the MOSES analysis
    :param session: The session object
    :param cwd: Current working directory to store the results of the analysis
    :param db: A reference to the mongo database
    :return:
    """
    setup_logging()
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")

    cwd, file_path = write_dataset(kwargs["dataset"], kwargs["mnemonic"])

    session = Session(kwargs["id"], kwargs["moses_options"], kwargs["crossval_options"],
                      file_path, kwargs["mnemonic"], kwargs["target_feature"])

    session.save(db)

    session.status = 1
    session.progress = 1
    session.start_time = time.time()
    session.update_session(db)

    try:
        moses_cross_val = CrossValidation(session, db, cwd)
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