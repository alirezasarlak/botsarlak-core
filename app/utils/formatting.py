def progress_bar(percent: float, width: int = 12) -> str:
    percent = max(0.0, min(1.0, percent))
    filled = int(percent * width)
    return "█" * filled + "░" * (width - filled)

def format_profile(u: dict) -> str:
    lines = [
        "👤 پروفایل",
        f"نام: {u.get('first_name','')} @{u.get('username','')}",
        f"رشته: {u.get('major','-')}",
        f"نام مستعار: {u.get('nickname','-')}",
        f"امتیاز: {u.get('points',0)}",
    ]
    return "\n".join(lines)

def format_board(rows: list[dict]) -> str:
    out = ["🏆 لیگ — ۱۰ نفر برتر"]
    for i, r in enumerate(rows, 1):
        out.append(f"{i}. {r.get('nickname','N/A')} — {r.get('points',0)} امتیاز")
    return "\n".join(out)
