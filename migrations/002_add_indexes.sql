CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_flash_user ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS idx_review_user ON review_calendar(user_id);
CREATE INDEX IF NOT EXISTS idx_points_user ON points_history(user_id);
