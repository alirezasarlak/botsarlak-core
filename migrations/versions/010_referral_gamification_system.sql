-- Referral and Gamification System for SarlakBot
-- Professional viral growth system with token rewards
-- Date: 2025-10-20

-- ==================== REFERRAL SYSTEM TABLES ====================

-- User Referrals Table
CREATE TABLE IF NOT EXISTS user_referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    referred_user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    referral_status VARCHAR(20) DEFAULT 'pending', -- pending, completed, rewarded
    referral_level INTEGER DEFAULT 1, -- for multi-level referrals
    points_earned INTEGER DEFAULT 0,
    tokens_earned INTEGER DEFAULT 0,
    referred_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    rewarded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(referrer_user_id, referred_user_id)
);

-- Referral Codes Table
CREATE TABLE IF NOT EXISTS referral_codes (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    total_uses INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 0, -- 0 means unlimited
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, code)
);

-- Referral Rewards Table
CREATE TABLE IF NOT EXISTS referral_rewards (
    id SERIAL PRIMARY KEY,
    reward_type VARCHAR(50) NOT NULL, -- direct, milestone, bonus
    reward_name VARCHAR(100) NOT NULL,
    reward_description TEXT,
    referral_count_required INTEGER DEFAULT 1,
    points_reward INTEGER DEFAULT 0,
    tokens_reward INTEGER DEFAULT 0,
    badge_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== TOKEN SYSTEM TABLES ====================

-- User Tokens Table
CREATE TABLE IF NOT EXISTS user_tokens (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_tokens INTEGER DEFAULT 0,
    available_tokens INTEGER DEFAULT 0,
    spent_tokens INTEGER DEFAULT 0,
    locked_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Token Transactions Table
CREATE TABLE IF NOT EXISTS token_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL, -- earn, spend, lock, unlock, transfer
    amount INTEGER NOT NULL,
    source VARCHAR(100) NOT NULL, -- referral, achievement, purchase, lottery
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lottery Entries Table
CREATE TABLE IF NOT EXISTS lottery_entries (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    lottery_id INTEGER NOT NULL,
    tokens_spent INTEGER NOT NULL,
    entry_count INTEGER DEFAULT 1,
    is_winner BOOLEAN DEFAULT FALSE,
    prize_amount DECIMAL(10, 2),
    prize_currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    drawn_at TIMESTAMPTZ
);

-- Lotteries Table
CREATE TABLE IF NOT EXISTS lotteries (
    id SERIAL PRIMARY KEY,
    lottery_name VARCHAR(100) NOT NULL,
    lottery_description TEXT,
    lottery_type VARCHAR(50) DEFAULT 'youtube_dollar', -- youtube_dollar, course, book
    prize_pool DECIMAL(10, 2) NOT NULL,
    prize_currency VARCHAR(10) DEFAULT 'USD',
    token_cost_per_entry INTEGER DEFAULT 10,
    max_entries_per_user INTEGER DEFAULT 100,
    total_entries INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, closed, drawn
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    drawn_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== GAMIFICATION ENHANCEMENTS ====================

-- Daily Quests Table
CREATE TABLE IF NOT EXISTS daily_quests (
    id SERIAL PRIMARY KEY,
    quest_name VARCHAR(100) NOT NULL,
    quest_description TEXT,
    quest_type VARCHAR(50) NOT NULL, -- study, referral, achievement, social
    quest_target INTEGER NOT NULL,
    points_reward INTEGER DEFAULT 0,
    tokens_reward INTEGER DEFAULT 0,
    difficulty VARCHAR(20) DEFAULT 'easy', -- easy, medium, hard, epic
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Quests Table
CREATE TABLE IF NOT EXISTS user_quests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    quest_id INTEGER NOT NULL REFERENCES daily_quests(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    is_claimed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    claimed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, quest_id, created_at::date)
);

-- Streaks Table (Enhanced)
CREATE TABLE IF NOT EXISTS user_streaks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    streak_type VARCHAR(50) NOT NULL, -- study, login, referral, quest
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_multiplier DECIMAL(3, 2) DEFAULT 1.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, streak_type)
);

-- Leaderboards Table
CREATE TABLE IF NOT EXISTS leaderboards (
    id SERIAL PRIMARY KEY,
    leaderboard_name VARCHAR(100) NOT NULL,
    leaderboard_type VARCHAR(50) NOT NULL, -- points, tokens, referrals, study_time
    period VARCHAR(20) DEFAULT 'weekly', -- daily, weekly, monthly, all_time
    top_count INTEGER DEFAULT 100,
    prize_pool INTEGER DEFAULT 0, -- in tokens
    status VARCHAR(20) DEFAULT 'active',
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leaderboard Entries Table
CREATE TABLE IF NOT EXISTS leaderboard_entries (
    id SERIAL PRIMARY KEY,
    leaderboard_id INTEGER NOT NULL REFERENCES leaderboards(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    rank INTEGER,
    prize_tokens INTEGER DEFAULT 0,
    is_prize_claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(leaderboard_id, user_id)
);

-- ==================== INDEXES ====================

-- Referral indexes
CREATE INDEX IF NOT EXISTS idx_user_referrals_referrer ON user_referrals(referrer_user_id);
CREATE INDEX IF NOT EXISTS idx_user_referrals_referred ON user_referrals(referred_user_id);
CREATE INDEX IF NOT EXISTS idx_user_referrals_status ON user_referrals(referral_status);
CREATE INDEX IF NOT EXISTS idx_referral_codes_user ON referral_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_referral_codes_code ON referral_codes(code);

-- Token indexes
CREATE INDEX IF NOT EXISTS idx_user_tokens_user ON user_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_token_transactions_user ON token_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_token_transactions_type ON token_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_lottery_entries_user ON lottery_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_lottery_entries_lottery ON lottery_entries(lottery_id);

-- Quest indexes
CREATE INDEX IF NOT EXISTS idx_user_quests_user ON user_quests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quests_quest ON user_quests(quest_id);
CREATE INDEX IF NOT EXISTS idx_user_quests_completed ON user_quests(is_completed);

-- Leaderboard indexes
CREATE INDEX IF NOT EXISTS idx_leaderboard_entries_leaderboard ON leaderboard_entries(leaderboard_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_entries_user ON leaderboard_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_entries_rank ON leaderboard_entries(rank);

-- ==================== TRIGGERS ====================

-- Update user_tokens updated_at
CREATE OR REPLACE FUNCTION update_user_tokens_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_tokens_updated_at
    BEFORE UPDATE ON user_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_user_tokens_updated_at();

-- Update leaderboard_entries updated_at
CREATE OR REPLACE FUNCTION update_leaderboard_entries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_leaderboard_entries_updated_at
    BEFORE UPDATE ON leaderboard_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_leaderboard_entries_updated_at();

-- ==================== INITIAL DATA ====================

-- Insert default referral rewards
INSERT INTO referral_rewards (reward_type, reward_name, reward_description, referral_count_required, points_reward, tokens_reward) VALUES
('direct', 'اولین دعوت', 'برای اولین دعوت موفق', 1, 100, 10),
('milestone', '5 دعوت', 'برای 5 دعوت موفق', 5, 500, 50),
('milestone', '10 دعوت', 'برای 10 دعوت موفق', 10, 1200, 120),
('milestone', '25 دعوت', 'برای 25 دعوت موفق', 25, 3500, 350),
('milestone', '50 دعوت', 'برای 50 دعوت موفق', 50, 8000, 800),
('milestone', '100 دعوت', 'برای 100 دعوت موفق', 100, 20000, 2000),
('bonus', 'دعوت‌کننده برتر', 'برای بیشترین دعوت در هفته', 0, 5000, 500)
ON CONFLICT DO NOTHING;

-- Insert default daily quests
INSERT INTO daily_quests (quest_name, quest_description, quest_type, quest_target, points_reward, tokens_reward, difficulty) VALUES
('مطالعه روزانه', '30 دقیقه مطالعه کن', 'study', 30, 50, 5, 'easy'),
('دعوت دوست', 'یک دوست دعوت کن', 'referral', 1, 100, 10, 'medium'),
('تکمیل آزمون', 'یک آزمون تکمیل کن', 'achievement', 1, 75, 7, 'medium'),
('مطالعه فشرده', '2 ساعت مطالعه کن', 'study', 120, 200, 20, 'hard'),
('دعوت گروهی', '3 دوست دعوت کن', 'referral', 3, 500, 50, 'epic')
ON CONFLICT DO NOTHING;

-- Insert default lottery
INSERT INTO lotteries (lottery_name, lottery_description, lottery_type, prize_pool, token_cost_per_entry, max_entries_per_user, ends_at) VALUES
('قرعه‌کشی ماهانه دلار یوتیوب', 'برنده 100 دلار یوتیوب می‌شه!', 'youtube_dollar', 100.00, 10, 100, NOW() + INTERVAL '30 days')
ON CONFLICT DO NOTHING;

-- ==================== VIEWS ====================

-- View for user referral stats
CREATE OR REPLACE VIEW user_referral_stats AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    COUNT(DISTINCT ur.id) as total_referrals,
    COUNT(DISTINCT CASE WHEN ur.referral_status = 'completed' THEN ur.id END) as completed_referrals,
    SUM(ur.points_earned) as total_points_from_referrals,
    SUM(ur.tokens_earned) as total_tokens_from_referrals,
    rc.code as referral_code
FROM users u
LEFT JOIN user_referrals ur ON u.user_id = ur.referrer_user_id
LEFT JOIN referral_codes rc ON u.user_id = rc.user_id AND rc.is_active = TRUE
GROUP BY u.user_id, rc.code;

-- View for top referrers
CREATE OR REPLACE VIEW top_referrers AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    COUNT(DISTINCT ur.id) as referral_count,
    SUM(ur.tokens_earned) as total_tokens,
    ROW_NUMBER() OVER (ORDER BY COUNT(DISTINCT ur.id) DESC, SUM(ur.tokens_earned) DESC) as rank
FROM users u
INNER JOIN user_referrals ur ON u.user_id = ur.referrer_user_id
WHERE ur.referral_status = 'completed'
GROUP BY u.user_id
ORDER BY referral_count DESC, total_tokens DESC
LIMIT 100;

-- View for user token balance
CREATE OR REPLACE VIEW user_token_balance AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    COALESCE(ut.total_tokens, 0) as total_tokens,
    COALESCE(ut.available_tokens, 0) as available_tokens,
    COALESCE(ut.spent_tokens, 0) as spent_tokens,
    COALESCE(ut.locked_tokens, 0) as locked_tokens
FROM users u
LEFT JOIN user_tokens ut ON u.user_id = ut.user_id;


