from telegram.ext import ApplicationBuilder, AIORateLimiter
from app.config import Config
from app.handlers.start import start_conv
from app.handlers.profile import profile_conv
from app.handlers.report import report_conv
from app.handlers.flashcards import flashcards_conv
from app.handlers.league import league_conv
from app.handlers.missions import missions_conv
from app.handlers.referrals import referrals_conv
from app.handlers.admin import admin_conv
from app.scheduler import setup_jobs

def build_application():
    app = ApplicationBuilder().token(Config.BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
    app.add_handler(start_conv)
    app.add_handler(profile_conv)
    app.add_handler(report_conv)
    app.add_handler(flashcards_conv)
    app.add_handler(league_conv)
    app.add_handler(missions_conv)
    app.add_handler(referrals_conv)
    app.add_handler(admin_conv)
    setup_jobs(app.job_queue)
    return app
