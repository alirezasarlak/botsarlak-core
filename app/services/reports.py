from app.models.study import add_entry, end_session, start_session
from app.models.users import add_points


def start_report(user_id: int) -> int:
    return start_session(user_id)


def finalize_report(
    user_id: int, session_id: int, entries: list[dict]
) -> tuple[int, int, int]:
    total_dur = 0
    total_tests = 0
    for e in entries:
        add_entry(
            session_id,
            e["subject"],
            e["topic"],
            e["tests"],
            e.get("notes", ""),
            e["dur"],
        )
        total_dur += e["dur"]
        total_tests += e["tests"]
    end_session(session_id)
    pts = total_dur // 30 + total_tests // 10
    if pts:
        add_points(user_id, pts, "گزارش روزانه")
    return total_dur, total_tests, pts
