from app.db import execute_query
def snapshot_day():
    data = execute_query("SELECT id, COALESCE(nickname, username) AS nickname, points FROM users ORDER BY points DESC", fetch="all")
    execute_query("INSERT INTO league_snapshots (period, data) VALUES (%s, %s)", ("day", data), commit=True)
def board_top(major: str | None = None, limit: int = 10):
    if major:
        return execute_query("SELECT COALESCE(nickname, username) AS nickname, points FROM users WHERE major=%s ORDER BY points DESC LIMIT %s",
                             (major, limit), fetch="all")
    return execute_query("SELECT COALESCE(nickname, username) AS nickname, points FROM users ORDER BY points DESC LIMIT %s",
                         (limit,), fetch="all")
