from app.db import execute_query
def referral_link(user_id: int) -> str:
    return f"https://t.me/Sarlak_academybot?start=ref{user_id}"
def apply_referral(referrer_id: int, new_user_id: int):
    execute_query("INSERT INTO referrals (referrer_id, new_user_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                  (referrer_id, new_user_id), commit=True)
    execute_query("UPDATE users SET points = points + 20 WHERE id=%s", (referrer_id,), commit=True)
