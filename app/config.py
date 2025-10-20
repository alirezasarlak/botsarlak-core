import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TZ = os.getenv("TZ", "Asia/Tehran")

    @classmethod
    def validate(cls):
        missing = [k for k in ["BOT_TOKEN","ADMIN_ID","DB_NAME","DB_USER","DB_PASSWORD"] if not os.getenv(k)]
        if missing:
            raise ValueError(f"Missing env vars: {missing}")
Config.validate()
