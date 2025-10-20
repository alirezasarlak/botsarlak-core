import logging
from app.config import Config

logger = logging.getLogger("sarlakbot")
def setup_logging():
    level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=level,
    )
    logger.setLevel(level)
