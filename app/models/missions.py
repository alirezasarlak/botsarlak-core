from app.db import execute_query
def today_missions(user_id: int):
    # Simple daily missions
    return [
        {"code":"study60","title":"۶۰ دقیقه مطالعه","xp":30},
        {"code":"tests30","title":"۳۰ تست امروز","xp":20},
        {"code":"flash5","title":"۵ فلش‌کارت مرور","xp":15},
    ]
def finish_mission(user_id: int, code: str):
    execute_query("INSERT INTO missions_done (user_id, code) VALUES (%s,%s) ON CONFLICT DO NOTHING", (user_id, code), commit=True)
    execute_query("UPDATE users SET points = points + 10 WHERE id=%s", (user_id,), commit=True)
