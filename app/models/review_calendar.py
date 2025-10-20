from app.db import execute_query
def create_review(user_id: int, target_type: str, target_id: str, review_date):
    execute_query("INSERT INTO review_calendar (user_id, type, target, review_date) VALUES (%s,%s,%s,%s)",
                  (user_id, target_type, target_id, review_date), commit=True)
def get_reviews(user_id: int, done: bool = False):
    return execute_query("SELECT * FROM review_calendar WHERE user_id=%s AND done=%s ORDER BY review_date ASC",
                         (user_id, done), fetch="all")
def mark_done(review_id: int):
    execute_query("UPDATE review_calendar SET done=TRUE WHERE id=%s", (review_id,), commit=True)
