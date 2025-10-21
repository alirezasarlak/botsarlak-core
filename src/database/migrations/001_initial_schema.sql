-- 🌌 SarlakBot v3.0 - Initial Database Schema
-- Gen-Z Cosmic Study Journey Database
-- Created: 2025-10-18
-- Version: 3.0.0

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    real_name VARCHAR(255),
    nickname VARCHAR(255) UNIQUE,
    nickname_changes_left INTEGER DEFAULT 3,
    phone VARCHAR(20),
    study_track VARCHAR(50),
    grade_band VARCHAR(50),
    grade_year VARCHAR(50),
    is_channel_member BOOLEAN DEFAULT FALSE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW()
);

-- ==================== USER PROFILES TABLE ====================
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    xp_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    total_study_time INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_study_date DATE,
    achievements_count INTEGER DEFAULT 0,
    preferences JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==================== STUDY SESSIONS TABLE ====================
CREATE TABLE IF NOT EXISTS study_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    subject VARCHAR(100),
    chapter VARCHAR(100),
    duration_minutes INTEGER,
    session_type VARCHAR(50) DEFAULT 'manual',
    mood VARCHAR(50),
    notes TEXT,
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== STUDY REPORTS TABLE ====================
CREATE TABLE IF NOT EXISTS study_reports (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    subject VARCHAR(100),
    chapter VARCHAR(100),
    activity_type VARCHAR(50),
    test_count INTEGER DEFAULT 0,
    mood VARCHAR(50),
    notes TEXT,
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== ACHIEVEMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    xp_reward INTEGER DEFAULT 0,
    requirements JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== USER ACHIEVEMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    achievement_id INTEGER REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- ==================== COMPETITIONS TABLE ====================
CREATE TABLE IF NOT EXISTS competitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'study',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== COMPETITION PARTICIPANTS TABLE ====================
CREATE TABLE IF NOT EXISTS competition_participants (
    id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES competitions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    score INTEGER DEFAULT 0,
    rank INTEGER,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(competition_id, user_id)
);

-- ==================== LEADERBOARDS TABLE ====================
CREATE TABLE IF NOT EXISTS leaderboards (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    score INTEGER DEFAULT 0,
    rank INTEGER,
    period VARCHAR(50) DEFAULT 'all_time',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, type, period)
);

-- ==================== CONTENT LESSONS TABLE ====================
CREATE TABLE IF NOT EXISTS content_lessons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    subject VARCHAR(100),
    grade_level VARCHAR(50),
    difficulty VARCHAR(50) DEFAULT 'medium',
    lesson_type VARCHAR(50) DEFAULT 'text',
    media_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== USER PROGRESS TABLE ====================
CREATE TABLE IF NOT EXISTS user_progress (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES content_lessons(id) ON DELETE CASCADE,
    progress_percentage INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    time_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, lesson_id)
);

-- ==================== FLASHCARDS TABLE ====================
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    subject VARCHAR(100),
    difficulty VARCHAR(50) DEFAULT 'medium',
    created_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== FLASHCARD DECKS TABLE ====================
CREATE TABLE IF NOT EXISTS flashcard_decks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    created_by BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    card_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== DECK CARDS TABLE ====================
CREATE TABLE IF NOT EXISTS deck_cards (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES flashcard_decks(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES flashcards(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(deck_id, card_id)
);

-- ==================== USER FLASHCARD PROGRESS TABLE ====================
CREATE TABLE IF NOT EXISTS user_flashcard_progress (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES flashcards(id) ON DELETE CASCADE,
    difficulty_level INTEGER DEFAULT 0,
    next_review TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, card_id)
);

-- ==================== ADMIN LOGS TABLE ====================
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    target_user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== SYSTEM LOGS TABLE ====================
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100),
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== FEATURE FLAGS TABLE ====================
CREATE TABLE IF NOT EXISTS feature_flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    target_users JSONB DEFAULT '[]',
    target_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==================== NOTIFICATIONS TABLE ====================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== INDEXES ====================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity);
CREATE INDEX IF NOT EXISTS idx_users_study_track ON users(study_track);

-- Study sessions indexes
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_created_at ON study_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_study_sessions_subject ON study_sessions(subject);

-- Study reports indexes
CREATE INDEX IF NOT EXISTS idx_study_reports_user_id ON study_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_study_reports_created_at ON study_reports(created_at);

-- Achievements indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement_id ON user_achievements(achievement_id);

-- Competitions indexes
CREATE INDEX IF NOT EXISTS idx_competition_participants_competition_id ON competition_participants(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_participants_user_id ON competition_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_competition_participants_score ON competition_participants(score);

-- Leaderboards indexes
CREATE INDEX IF NOT EXISTS idx_leaderboards_user_id ON leaderboards(user_id);
CREATE INDEX IF NOT EXISTS idx_leaderboards_type ON leaderboards(type);
CREATE INDEX IF NOT EXISTS idx_leaderboards_period ON leaderboards(period);
CREATE INDEX IF NOT EXISTS idx_leaderboards_score ON leaderboards(score);

-- Content indexes
CREATE INDEX IF NOT EXISTS idx_content_lessons_subject ON content_lessons(subject);
CREATE INDEX IF NOT EXISTS idx_content_lessons_grade_level ON content_lessons(grade_level);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_lesson_id ON user_progress(lesson_id);

-- Flashcard indexes
CREATE INDEX IF NOT EXISTS idx_flashcards_subject ON flashcards(subject);
CREATE INDEX IF NOT EXISTS idx_flashcard_decks_created_by ON flashcard_decks(created_by);
CREATE INDEX IF NOT EXISTS idx_user_flashcard_progress_user_id ON user_flashcard_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_flashcard_progress_next_review ON user_flashcard_progress(next_review);

-- Log indexes
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at ON admin_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- ==================== TRIGGERS ====================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_flashcard_progress_updated_at BEFORE UPDATE ON user_flashcard_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feature_flags_updated_at BEFORE UPDATE ON feature_flags FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== INITIAL DATA ====================

-- Insert default achievements
INSERT INTO achievements (name, description, icon, xp_reward, requirements) VALUES
('🌱 اولین قدم', 'اولین جلسه مطالعه خود را تکمیل کردید', '🌱', 10, '{"study_sessions": 1}'),
('🔥 استقامت', '7 روز متوالی مطالعه کردید', '🔥', 50, '{"streak_days": 7}'),
('⚡ سرعت', 'در یک روز 5 جلسه مطالعه کردید', '⚡', 30, '{"daily_sessions": 5}'),
('🎯 هدفمند', '100 جلسه مطالعه تکمیل کردید', '🎯', 100, '{"study_sessions": 100}'),
('🏆 قهرمان', 'در رتبه اول یک رقابت قرار گرفتید', '🏆', 200, '{"first_place": 1}'),
('📚 دانشجو', '10 درس را تکمیل کردید', '📚', 75, '{"completed_lessons": 10}'),
('🧠 حافظه', '100 فلش‌کارت را مرور کردید', '🧠', 80, '{"reviewed_cards": 100}'),
('💎 الماس', '1000 امتیاز XP کسب کردید', '💎', 150, '{"total_xp": 1000}');

-- Insert default feature flags
INSERT INTO feature_flags (name, description, is_enabled) VALUES
('onboarding_v1', 'Onboarding system version 1', true),
('profile_v1', 'Profile system version 1', true),
('report_v1', 'Study report system version 1', true),
('motivation_v1', 'Motivation system version 1', true),
('competition_v1', 'Competition system version 1', true),
('store_v1', 'Store system version 1', true),
('ai_coach_v1', 'AI Coach system version 1', false),
('social_features_v1', 'Social features version 1', false);

-- ==================== COMMENTS ====================

COMMENT ON TABLE users IS 'Main users table with basic information and onboarding data';
COMMENT ON TABLE user_profiles IS 'Extended user profiles with gamification data';
COMMENT ON TABLE study_sessions IS 'User study sessions tracking';
COMMENT ON TABLE study_reports IS 'Manual study reports from users';
COMMENT ON TABLE achievements IS 'Available achievements in the system';
COMMENT ON TABLE user_achievements IS 'User earned achievements';
COMMENT ON TABLE competitions IS 'Competition events';
COMMENT ON TABLE competition_participants IS 'Users participating in competitions';
COMMENT ON TABLE leaderboards IS 'User rankings and scores';
COMMENT ON TABLE content_lessons IS 'Educational content lessons';
COMMENT ON TABLE user_progress IS 'User progress through lessons';
COMMENT ON TABLE flashcards IS 'Flashcard content';
COMMENT ON TABLE flashcard_decks IS 'Collections of flashcards';
COMMENT ON TABLE deck_cards IS 'Cards belonging to decks';
COMMENT ON TABLE user_flashcard_progress IS 'User progress with flashcards (SRS)';
COMMENT ON TABLE admin_logs IS 'Admin actions logging';
COMMENT ON TABLE system_logs IS 'System events logging';
COMMENT ON TABLE feature_flags IS 'Feature flags for A/B testing';
COMMENT ON TABLE notifications IS 'User notifications';

-- ==================== VERSION INFO ====================

-- Create version tracking table
CREATE TABLE IF NOT EXISTS schema_versions (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_versions (version, description) VALUES 
('3.0.0', 'Initial schema for SarlakBot v3.0 - Gen-Z Cosmic Study Journey')
ON CONFLICT (version) DO NOTHING;




