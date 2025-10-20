from app.models.flashcards import bump_count
from app.models.review_calendar import create_review
from app.db import execute_query
from app.utils.time_utils import srs_next

def schedule_review(user_id: int, card_id: int, correct: bool):
    inc = 1 if correct else -1
    bump_count(card_id, inc)
    cnt = execute_query("SELECT correct_count FROM flashcards WHERE id=%s", (card_id,), fetch="one")["correct_count"]
    create_review(user_id, "flashcard", str(card_id), srs_next(cnt))
