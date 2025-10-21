-- Simple Gamification System Tables

-- Create user_quests table with simple syntax
CREATE TABLE IF NOT EXISTS user_quests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    quest_id INTEGER NOT NULL REFERENCES daily_quests(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    is_claimed BOOLEAN DEFAULT FALSE,
    claimed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_streaks table
CREATE TABLE IF NOT EXISTS user_streaks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    streak_type VARCHAR(50) NOT NULL,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_multiplier DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_tokens table
CREATE TABLE IF NOT EXISTS user_tokens (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_tokens INTEGER DEFAULT 0,
    available_tokens INTEGER DEFAULT 0,
    spent_tokens INTEGER DEFAULT 0,
    locked_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create token_transactions table
CREATE TABLE IF NOT EXISTS token_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,
    amount INTEGER NOT NULL,
    source VARCHAR(100),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create lotteries table
CREATE TABLE IF NOT EXISTS lotteries (
    id SERIAL PRIMARY KEY,
    lottery_name VARCHAR(100) NOT NULL,
    lottery_description TEXT,
    prize_pool INTEGER NOT NULL,
    prize_currency VARCHAR(10) DEFAULT 'USD',
    token_cost_per_entry INTEGER NOT NULL,
    max_entries_per_user INTEGER DEFAULT 1,
    total_entries INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ NOT NULL,
    drawn_at TIMESTAMPTZ,
    winner_user_id BIGINT REFERENCES users(user_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create lottery_entries table
CREATE TABLE IF NOT EXISTS lottery_entries (
    id SERIAL PRIMARY KEY,
    lottery_id INTEGER NOT NULL REFERENCES lotteries(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    entry_count INTEGER DEFAULT 1,
    tokens_spent INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_quests_user_id ON user_quests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quests_quest_id ON user_quests(quest_id);
CREATE INDEX IF NOT EXISTS idx_user_streaks_user_id ON user_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_token_transactions_user_id ON token_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_lotteries_is_active ON lotteries(is_active);
CREATE INDEX IF NOT EXISTS idx_lottery_entries_lottery_id ON lottery_entries(lottery_id);

-- Insert sample daily quests
INSERT INTO daily_quests (quest_name, quest_description, quest_type, quest_target, points_reward, tokens_reward, difficulty) VALUES
('مطالعه روزانه', '30 دقیقه مطالعه کن', 'study', 30, 50, 5, 'easy'),
('دعوت دوست', 'یک دوست دعوت کن', 'referral', 1, 100, 10, 'easy'),
('ورود روزانه', 'هر روز وارد ربات شو', 'login', 1, 20, 2, 'easy'),
('تکمیل پروفایل', 'پروفایل خودت رو کامل کن', 'profile', 1, 30, 3, 'easy'),
('شرکت در رقابت', 'در یک رقابت شرکت کن', 'competition', 1, 75, 8, 'medium')
ON CONFLICT DO NOTHING;

-- Insert sample lottery
INSERT INTO lotteries (lottery_name, lottery_description, prize_pool, token_cost_per_entry, ends_at) VALUES
('قرعه‌کشی هفتگی', 'قرعه‌کشی هفتگی با جایزه 100 دلار', 100, 50, NOW() + INTERVAL '7 days')
ON CONFLICT DO NOTHING;
