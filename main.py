from dotenv import load_dotenv
load_dotenv()

from app.utils.logger import setup_logging, logger
from app.db import run_migrations
from app.bot import build_application

if __name__ == "__main__":
    setup_logging()
    logger.info("Running DB migrations...")
    run_migrations()
    logger.info("Starting application...")
    app = build_application()
    app.run_polling(drop_pending_updates=True)
