__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from celery import Celery
from celery.utils.log import get_task_logger
import pymongo
from config import MONGODB_URI, CELERY_OPTS, DB_NAME
import time
from crossval.moses_cross_val import CrossValidation
from models.dbmodels import Session

celery = Celery('mozi_snet', broker=CELERY_OPTS["CELERY_BROKER_URL"])
celery.conf.update(CELERY_OPTS)

logger = get_task_logger(__name__)


@celery.task
def start_analysis(**kwargs):
    """
    A celery task that runs the MOSES analysis
    :param session: The session object
    :param cwd: Current working directory to store the results of the analysis
    :param db: A reference to the mongo database
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]

    session = Session(kwargs["id"], kwargs["moses_options"], kwargs["crossval_options"],
                      kwargs["dataset"], kwargs["mnemonic"], kwargs["target_feature"])

    cwd = kwargs["cwd"]

    session.status = 1
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
        logger.error(f"Task failed with {e.__str__()}")

    finally:
        session.end_time = time.time()
        session.update_session(db)