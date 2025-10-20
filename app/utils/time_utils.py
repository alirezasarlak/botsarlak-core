from datetime import datetime, timedelta, date
from jdatetime import datetime as jdt
from zoneinfo import ZoneInfo
from app.config import Config

TZ = ZoneInfo(Config.TZ)
def now(): return datetime.now(TZ)
def jalali(dt: datetime | None = None) -> str:
    dt = dt or now()
    return jdt.fromgregorian(datetime=dt).strftime("%Y/%m/%d")
def minutes_between(a: datetime, b: datetime) -> int:
    return int((b - a).total_seconds() // 60)
def srs_next(correct_count: int) -> date:
    steps = [1, 3, 7, 14, 30]
    return (now().date() + timedelta(days=steps[min(correct_count, len(steps)-1)]))
