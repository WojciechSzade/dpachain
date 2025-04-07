import logging

from pymongo import MongoClient
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

# @retry(
#     stop=stop_after_attempt(max_tries),
#     wait=wait_fixed(wait_seconds),
#     before=before_log(logger, logging.INFO),
#     after=after_log(logger, logging.WARN),
# )
def init_db(mongodb_url: str):
    client = MongoClient(mongodb_url)
    try:
        client.server_info()
    except Exception as e:
        logger.error(e)
        raise e
    logger.info("Connection to MongoDB established")
    return client
