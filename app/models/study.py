from app.db import execute_query
from app.utils.time_utils import jalali, now


def start_session(user_id: int):
    r = execute_query(
        "INSERT INTO study_sessions (user_id, day_jalali, start_dt) VALUES (%s,%s,%s) RETURNING id",
        (user_id, jalali(), now()),
        fetch="one",
        commit=True,
    )
    return r["id"]


def end_session(session_id: int):
    execute_query(
        "UPDATE study_sessions SET end_dt = NOW() WHERE id=%s",
        (session_id,),
        commit=True,
    )


def add_entry(
    session_id: int, subject: str, topic: str, tests: int, notes: str, dur: int
):
    execute_query(
        "INSERT INTO study_entries (session_id, subject, topic, tests, notes, dur) VALUES (%s,%s,%s,%s,%s,%s)",
        (session_id, subject, topic, tests, notes, dur),
        commit=True,
    )
