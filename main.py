from dotenv import load_dotenv

load_dotenv()

from app.bot import build_application
from app.db import run_migrations
from app.utils.logger import logger, setup_logging

if __name__ == "__main__":
    setup_logging()
    logger.info("Running DB migrations...")
    run_migrations()
    logger.info("Starting application...")
    app = build_application()
    app.run_polling(drop_pending_updates=True)
