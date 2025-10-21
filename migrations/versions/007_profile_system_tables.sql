-- Profile System Tables for SarlakBot v3.1.0
-- Comprehensive profile management with gamification

-- ==================== USER PROFILES TABLE ====================
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    nickname VARCHAR(50),
    bio TEXT,
    avatar_url TEXT,
    phone_number VARCHAR(20),
    birth_date DATE,
    study_track VARCHAR(50),
    grade_level VARCHAR(20),
    grade_year INTEGER,
    privacy_level VARCHAR(20) DEFAULT 'friends_only',
    is_public BOOLEAN DEFAULT FALSE,
    show_statistics BOOLEAN DEFAULT TRUE,
    show_achievements BOOLEAN DEFAULT TRUE,
    show_streak BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== USER STATISTICS TABLE ====================
CREATE TABLE IF NOT EXISTS user_statistics (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    total_study_time INTEGER DEFAULT 0, -- in minutes
    daily_study_time INTEGER DEFAULT 0, -- in minutes
    weekly_study_time INTEGER DEFAULT 0, -- in minutes
    monthly_study_time INTEGER DEFAULT 0, -- in minutes
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    completed_goals INTEGER DEFAULT 0,
    total_goals INTEGER DEFAULT 0,
    study_days INTEGER DEFAULT 0,
    last_study_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- ==================== USER GOALS TABLE ====================
CREATE TABLE IF NOT EXISTS user_goals (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    goal_value INTEGER NOT NULL, -- target value
    current_value INTEGER DEFAULT 0, -- current progress
    goal_unit VARCHAR(20) NOT NULL, -- 'minutes', 'sessions', 'days'
    goal_title VARCHAR(100) NOT NULL,
    goal_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== USER ACHIEVEMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    achievement_id VARCHAR(100) NOT NULL,
    achievement_name VARCHAR(100) NOT NULL,
    achievement_description TEXT,
    achievement_type VARCHAR(50) NOT NULL, -- 'study', 'streak', 'goal', 'special'
    achievement_category VARCHAR(50) NOT NULL, -- 'bronze', 'silver', 'gold', 'platinum'
    points_awarded INTEGER DEFAULT 0,
    badge_icon VARCHAR(20),
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),
    is_featured BOOLEAN DEFAULT FALSE,
    
    UNIQUE(user_id, achievement_id)
);

-- ==================== USER LEVELS TABLE ====================
CREATE TABLE IF NOT EXISTS user_levels (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    current_level INTEGER DEFAULT 1,
    total_points INTEGER DEFAULT 0,
    level_points INTEGER DEFAULT 0, -- points in current level
    next_level_points INTEGER DEFAULT 100, -- points needed for next level
    level_title VARCHAR(50) DEFAULT 'مبتدی',
    level_color VARCHAR(20) DEFAULT '#4CAF50',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- ==================== USER BADGES TABLE ====================
CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    badge_id VARCHAR(100) NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    badge_description TEXT,
    badge_icon VARCHAR(20),
    badge_color VARCHAR(20),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    is_displayed BOOLEAN DEFAULT TRUE,
    
    UNIQUE(user_id, badge_id)
);

-- ==================== ACHIEVEMENT DEFINITIONS TABLE ====================
CREATE TABLE IF NOT EXISTS achievement_definitions (
    id SERIAL PRIMARY KEY,
    achievement_id VARCHAR(100) UNIQUE NOT NULL,
    achievement_name VARCHAR(100) NOT NULL,
    achievement_description TEXT,
    achievement_type VARCHAR(50) NOT NULL,
    achievement_category VARCHAR(50) NOT NULL,
    points_awarded INTEGER DEFAULT 0,
    badge_icon VARCHAR(20),
    requirements JSONB NOT NULL, -- conditions to unlock
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_privacy ON user_profiles(privacy_level);
CREATE INDEX IF NOT EXISTS idx_user_profiles_public ON user_profiles(is_public);

-- User statistics indexes
CREATE INDEX IF NOT EXISTS idx_user_statistics_user_id ON user_statistics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_statistics_streak ON user_statistics(current_streak);
CREATE INDEX IF NOT EXISTS idx_user_statistics_study_time ON user_statistics(total_study_time);

-- User goals indexes
CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_user_goals_type ON user_goals(goal_type);
CREATE INDEX IF NOT EXISTS idx_user_goals_active ON user_goals(is_active);
CREATE INDEX IF NOT EXISTS idx_user_goals_completed ON user_goals(is_completed);

-- User achievements indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_type ON user_achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_user_achievements_category ON user_achievements(achievement_category);
CREATE INDEX IF NOT EXISTS idx_user_achievements_unlocked ON user_achievements(unlocked_at);

-- User levels indexes
CREATE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id);
CREATE INDEX IF NOT EXISTS idx_user_levels_level ON user_levels(current_level);
CREATE INDEX IF NOT EXISTS idx_user_levels_points ON user_levels(total_points);

-- User badges indexes
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_earned ON user_badges(earned_at);

-- Achievement definitions indexes
CREATE INDEX IF NOT EXISTS idx_achievement_definitions_id ON achievement_definitions(achievement_id);
CREATE INDEX IF NOT EXISTS idx_achievement_definitions_type ON achievement_definitions(achievement_type);
CREATE INDEX IF NOT EXISTS idx_achievement_definitions_active ON achievement_definitions(is_active);

-- ==================== TRIGGERS ====================
-- Update timestamp trigger for user_profiles
CREATE OR REPLACE FUNCTION update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_profiles_updated_at();

-- Update timestamp trigger for user_statistics
CREATE OR REPLACE FUNCTION update_user_statistics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_statistics_updated_at
    BEFORE UPDATE ON user_statistics
    FOR EACH ROW
    EXECUTE FUNCTION update_user_statistics_updated_at();

-- Update timestamp trigger for user_goals
CREATE OR REPLACE FUNCTION update_user_goals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_goals_updated_at
    BEFORE UPDATE ON user_goals
    FOR EACH ROW
    EXECUTE FUNCTION update_user_goals_updated_at();

-- Update timestamp trigger for user_levels
CREATE OR REPLACE FUNCTION update_user_levels_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_levels_updated_at
    BEFORE UPDATE ON user_levels
    FOR EACH ROW
    FOR EACH ROW
    EXECUTE FUNCTION update_user_levels_updated_at();

-- ==================== INITIAL DATA ====================
-- Insert default achievement definitions
INSERT INTO achievement_definitions (achievement_id, achievement_name, achievement_description, achievement_type, achievement_category, points_awarded, badge_icon, requirements) VALUES
-- Study time achievements
('study_1_hour', 'اولین ساعت مطالعه', 'اولین ساعت مطالعه خود را تکمیل کنید', 'study', 'bronze', 10, '⏰', '{"total_study_time": 60}'),
('study_10_hours', '10 ساعت مطالعه', '10 ساعت مطالعه کنید', 'study', 'silver', 50, '📚', '{"total_study_time": 600}'),
('study_100_hours', '100 ساعت مطالعه', '100 ساعت مطالعه کنید', 'study', 'gold', 200, '🎓', '{"total_study_time": 6000}'),
('study_1000_hours', '1000 ساعت مطالعه', '1000 ساعت مطالعه کنید', 'study', 'platinum', 1000, '👑', '{"total_study_time": 60000}'),

-- Streak achievements
('streak_3_days', '3 روز متوالی', '3 روز متوالی مطالعه کنید', 'streak', 'bronze', 15, '🔥', '{"current_streak": 3}'),
('streak_7_days', 'یک هفته متوالی', '7 روز متوالی مطالعه کنید', 'streak', 'silver', 50, '🔥', '{"current_streak": 7}'),
('streak_30_days', 'یک ماه متوالی', '30 روز متوالی مطالعه کنید', 'streak', 'gold', 200, '🔥', '{"current_streak": 30}'),
('streak_100_days', '100 روز متوالی', '100 روز متوالی مطالعه کنید', 'streak', 'platinum', 1000, '🔥', '{"current_streak": 100}'),

-- Goal achievements
('goal_first', 'اولین هدف', 'اولین هدف خود را تکمیل کنید', 'goal', 'bronze', 20, '🎯', '{"completed_goals": 1}'),
('goal_10', '10 هدف', '10 هدف تکمیل کنید', 'goal', 'silver', 100, '🎯', '{"completed_goals": 10}'),
('goal_50', '50 هدف', '50 هدف تکمیل کنید', 'goal', 'gold', 500, '🎯', '{"completed_goals": 50}'),
('goal_100', '100 هدف', '100 هدف تکمیل کنید', 'goal', 'platinum', 2000, '🎯', '{"completed_goals": 100}'),

-- Special achievements
('early_bird', 'پرنده سحرخیز', 'قبل از 6 صبح مطالعه کنید', 'special', 'bronze', 25, '🌅', '{"study_before_6am": true}'),
('night_owl', 'جغد شب', 'بعد از 10 شب مطالعه کنید', 'special', 'bronze', 25, '🦉', '{"study_after_10pm": true}'),
('weekend_warrior', 'جنگجوی آخر هفته', 'در آخر هفته مطالعه کنید', 'special', 'silver', 50, '⚔️', '{"weekend_study": true}'),
('marathon_runner', 'دونده ماراتن', '5 ساعت متوالی مطالعه کنید', 'special', 'gold', 200, '🏃', '{"consecutive_study": 300}')

ON CONFLICT (achievement_id) DO NOTHING;

-- ==================== VIEWS ====================
-- View for user profile summary
CREATE OR REPLACE VIEW user_profile_summary AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    u.last_name,
    up.display_name,
    up.nickname,
    up.avatar_url,
    up.privacy_level,
    up.is_public,
    us.total_study_time,
    us.current_streak,
    us.longest_streak,
    us.total_sessions,
    ul.current_level,
    ul.total_points,
    ul.level_title,
    COUNT(ua.id) as total_achievements,
    COUNT(ub.id) as total_badges
FROM users u
LEFT JOIN user_profiles up ON u.user_id = up.user_id
LEFT JOIN user_statistics us ON u.user_id = us.user_id
LEFT JOIN user_levels ul ON u.user_id = ul.user_id
LEFT JOIN user_achievements ua ON u.user_id = ua.user_id
LEFT JOIN user_badges ub ON u.user_id = ub.user_id
GROUP BY u.user_id, up.display_name, up.nickname, up.avatar_url, up.privacy_level, up.is_public,
         us.total_study_time, us.current_streak, us.longest_streak, us.total_sessions,
         ul.current_level, ul.total_points, ul.level_title;

-- View for leaderboard
CREATE OR REPLACE VIEW leaderboard_view AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    up.display_name,
    up.nickname,
    us.total_study_time,
    us.current_streak,
    ul.current_level,
    ul.total_points,
    ROW_NUMBER() OVER (ORDER BY ul.total_points DESC, us.total_study_time DESC) as rank
FROM users u
LEFT JOIN user_profiles up ON u.user_id = up.user_id
LEFT JOIN user_statistics us ON u.user_id = us.user_id
LEFT JOIN user_levels ul ON u.user_id = ul.user_id
WHERE u.is_active = TRUE
ORDER BY ul.total_points DESC, us.total_study_time DESC;



