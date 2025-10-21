from app.db import execute_query


def create_card(user_id: int, subject: str, q: str, a: str):
    r = execute_query(
        "INSERT INTO flashcards (user_id, subject, question, answer) VALUES (%s,%s,%s,%s) RETURNING id",
        (user_id, subject, q, a),
        fetch="one",
        commit=True,
    )
    return r["id"]


def list_due(user_id: int):
    return execute_query(
        "SELECT * FROM flashcards WHERE user_id=%s AND needs_review=TRUE",
        (user_id,),
        fetch="all",
    )


def bump_count(card_id: int, inc: int):
    execute_query(
        "UPDATE flashcards SET correct_count = GREATEST(0, correct_count + %s), needs_review = (correct_count + %s < 5) WHERE id=%s",
        (inc, inc, card_id),
        commit=True,
    )
