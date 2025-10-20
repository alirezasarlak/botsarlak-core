from app.models.league import board_top, snapshot_day
def reset_league_daily(): snapshot_day()
def get_board(major: str | None = None): return board_top(major)
