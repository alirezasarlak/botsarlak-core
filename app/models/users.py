from app.db import execute_query


def ensure_user(user_id: int, username: str, first_name: str, last_name: str | None):
    execute_query(
        """
        INSERT INTO users (id, username, first_name, last_name)
        VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING
    """,
        (user_id, username, first_name, last_name),
        commit=True,
    )


def get_user(user_id: int):
    return execute_query("SELECT * FROM users WHERE id=%s", (user_id,), fetch="one")


def set_major(user_id: int, major: str):
    execute_query(
        "UPDATE users SET major=%s WHERE id=%s", (major, user_id), commit=True
    )


def set_nickname(user_id: int, nickname: str):
    execute_query(
        "UPDATE users SET nickname=%s WHERE id=%s", (nickname, user_id), commit=True
    )


def set_phone(user_id: int, phone: str):
    execute_query(
        "UPDATE users SET phone=%s WHERE id=%s", (phone, user_id), commit=True
    )


def add_points(user_id: int, delta: int, reason: str = ""):
    execute_query(
        "UPDATE users SET points = points + %s WHERE id=%s",
        (delta, user_id),
        commit=True,
    )
    execute_query(
        "INSERT INTO points_history (user_id, points, reason) VALUES (%s,%s,%s)",
        (user_id, delta, reason),
        commit=True,
    )


def top_users(limit: int = 10):
    return execute_query(
        "SELECT id, COALESCE(nickname, username) AS nickname, points FROM users ORDER BY points DESC LIMIT %s",
        (limit,),
        fetch="all",
    )
