from telegram.ext import JobQueue
from datetime import time
from zoneinfo import ZoneInfo
from app.config import Config
from app.services.league import reset_league_daily

TZ = ZoneInfo(Config.TZ)

async def job_league(context): reset_league_daily()

def setup_jobs(job_queue: JobQueue):
    job_queue.run_daily(job_league, time=time(0,5,tzinfo=TZ))
