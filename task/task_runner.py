__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from celery import Celery
from celery.utils.log import get_task_logger
from pymongo import MongoClient
from config import MONGODB_URI, CELERY_OPTS, DB_NAME
import time
from crossval.moses_cross_val import CrossValidation

celery = Celery('mozi_snet', broker=CELERY_OPTS["CELERY_BROKER_URL"])
celery.conf.update(CELERY_OPTS)

logger = get_task_logger(__name__)

@celery.task
def start_analysis(session, cwd, db=None):
    if not db:
        db = MongoClient(MONGODB_URI)[DB_NAME]

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
    except Exception as e:
        session.status = -1
        session.message = e.__str__()
        logger.error(f"Task failed with {e.__str__()}")

    finally:
        session.end_time = time.time()
        session.update_session(db)