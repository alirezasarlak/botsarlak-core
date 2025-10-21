-- Migration: League System
-- Version: 011
-- Date: 2025-10-20
-- Description: Complete league and competition system

-- Create leagues table
CREATE TABLE IF NOT EXISTS leagues (
    league_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'bronze', -- bronze, silver, gold, platinum, diamond, master, grandmaster, challenger
    league_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, seasonal
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    max_participants INTEGER NOT NULL DEFAULT 100,
    current_participants INTEGER DEFAULT 0,
    entry_requirements JSONB DEFAULT '{}',
    rewards JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create league participants table
CREATE TABLE IF NOT EXISTS league_participants (
    participant_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    league_id INTEGER NOT NULL REFERENCES leagues(league_id) ON DELETE CASCADE,
    rank INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    study_time INTEGER DEFAULT 0, -- in minutes
    tests_completed INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2) DEFAULT 0.00,
    streak INTEGER DEFAULT 0,
    joined_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, league_id)
);

-- Create league rewards log table
CREATE TABLE IF NOT EXISTS league_rewards_log (
    log_id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES leagues(league_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    reward_type VARCHAR(50) NOT NULL,
    reward_value TEXT NOT NULL,
    distributed_at TIMESTAMP DEFAULT NOW()
);

-- Create user rewards table
CREATE TABLE IF NOT EXISTS user_rewards (
    reward_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    reward_type VARCHAR(50) NOT NULL, -- points, badge, title, etc.
    reward_value TEXT NOT NULL,
    reward_description TEXT,
    source VARCHAR(50) DEFAULT 'system', -- league, achievement, daily, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create private leagues table
CREATE TABLE IF NOT EXISTS private_leagues (
    private_league_id SERIAL PRIMARY KEY,
    creator_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    invite_code VARCHAR(20) UNIQUE NOT NULL,
    max_participants INTEGER DEFAULT 20,
    current_participants INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    password VARCHAR(255), -- Optional password protection
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rewards JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create private league participants table
CREATE TABLE IF NOT EXISTS private_league_participants (
    participant_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    private_league_id INTEGER NOT NULL REFERENCES private_leagues(private_league_id) ON DELETE CASCADE,
    rank INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    study_time INTEGER DEFAULT 0,
    tests_completed INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2) DEFAULT 0.00,
    streak INTEGER DEFAULT 0,
    joined_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, private_league_id)
);

-- Create league challenges table
CREATE TABLE IF NOT EXISTS league_challenges (
    challenge_id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES leagues(league_id) ON DELETE CASCADE,
    challenge_name VARCHAR(255) NOT NULL,
    challenge_description TEXT,
    challenge_type VARCHAR(50) NOT NULL, -- study_time, test_count, accuracy, streak, etc.
    target_value INTEGER NOT NULL,
    reward_points INTEGER DEFAULT 0,
    reward_badge VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user challenge progress table
CREATE TABLE IF NOT EXISTS user_challenge_progress (
    progress_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    challenge_id INTEGER NOT NULL REFERENCES league_challenges(challenge_id) ON DELETE CASCADE,
    current_progress INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, challenge_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_leagues_active ON leagues(is_active, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_leagues_type ON leagues(league_type, is_active);
CREATE INDEX IF NOT EXISTS idx_league_participants_user ON league_participants(user_id, league_id);
CREATE INDEX IF NOT EXISTS idx_league_participants_rank ON league_participants(league_id, rank);
CREATE INDEX IF NOT EXISTS idx_league_participants_points ON league_participants(league_id, points DESC);
CREATE INDEX IF NOT EXISTS idx_league_rewards_log ON league_rewards_log(league_id, distributed_at);
CREATE INDEX IF NOT EXISTS idx_user_rewards_user ON user_rewards(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_private_leagues_creator ON private_leagues(creator_id, is_active);
CREATE INDEX IF NOT EXISTS idx_private_leagues_code ON private_leagues(invite_code);
CREATE INDEX IF NOT EXISTS idx_private_league_participants ON private_league_participants(user_id, private_league_id);
CREATE INDEX IF NOT EXISTS idx_league_challenges ON league_challenges(league_id, is_active);
CREATE INDEX IF NOT EXISTS idx_user_challenge_progress ON user_challenge_progress(user_id, challenge_id);

-- Create function to create daily league
CREATE OR REPLACE FUNCTION create_daily_league(p_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER AS $$
DECLARE
    league_id INTEGER;
    league_name VARCHAR(255);
BEGIN
    league_name := 'Daily League - ' || p_date::TEXT;
    
    INSERT INTO leagues (
        name, tier, league_type, start_date, end_date, max_participants,
        entry_requirements, rewards, is_active
    ) VALUES (
        league_name, 'bronze', 'daily', p_date, p_date,
        100, '{"entry_points": 0}', 
        '{"top_1": {"points": 100, "badge": "daily_champion"}, "top_3": {"points": 50, "badge": "daily_top3"}, "top_10": {"points": 25, "badge": "daily_top10"}}',
        TRUE
    ) RETURNING leagues.league_id INTO league_id;
    
    RETURN league_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to create weekly league
CREATE OR REPLACE FUNCTION create_weekly_league(p_start_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER AS $$
DECLARE
    league_id INTEGER;
    league_name VARCHAR(255);
    end_date DATE;
BEGIN
    end_date := p_start_date + INTERVAL '6 days';
    league_name := 'Weekly League - ' || p_start_date::TEXT || ' to ' || end_date::TEXT;
    
    INSERT INTO leagues (
        name, tier, league_type, start_date, end_date, max_participants,
        entry_requirements, rewards, is_active
    ) VALUES (
        league_name, 'silver', 'weekly', p_start_date, end_date,
        500, '{"entry_points": 100}', 
        '{"top_1": {"points": 500, "badge": "weekly_champion"}, "top_3": {"points": 300, "badge": "weekly_top3"}, "top_10": {"points": 150, "badge": "weekly_top10"}}',
        TRUE
    ) RETURNING leagues.league_id INTO league_id;
    
    RETURN league_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to create monthly league
CREATE OR REPLACE FUNCTION create_monthly_league(p_start_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER AS $$
DECLARE
    league_id INTEGER;
    league_name VARCHAR(255);
    end_date DATE;
BEGIN
    end_date := p_start_date + INTERVAL '29 days';
    league_name := 'Monthly League - ' || p_start_date::TEXT || ' to ' || end_date::TEXT;
    
    INSERT INTO leagues (
        name, tier, league_type, start_date, end_date, max_participants,
        entry_requirements, rewards, is_active
    ) VALUES (
        league_name, 'gold', 'monthly', p_start_date, end_date,
        1000, '{"entry_points": 500}', 
        '{"top_1": {"points": 2000, "badge": "monthly_champion"}, "top_3": {"points": 1200, "badge": "monthly_top3"}, "top_10": {"points": 600, "badge": "monthly_top10"}}',
        TRUE
    ) RETURNING leagues.league_id INTO league_id;
    
    RETURN league_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to update league standings
CREATE OR REPLACE FUNCTION update_league_standings(p_league_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Update participant stats from study reports
    UPDATE league_participants 
    SET 
        study_time = COALESCE((
            SELECT SUM(study_minutes) 
            FROM study_reports 
            WHERE user_id = league_participants.user_id 
            AND report_date >= (SELECT start_date FROM leagues WHERE league_id = p_league_id)
            AND report_date <= (SELECT end_date FROM leagues WHERE league_id = p_league_id)
        ), 0),
        tests_completed = COALESCE((
            SELECT SUM(tests_count) 
            FROM study_reports 
            WHERE user_id = league_participants.user_id 
            AND report_date >= (SELECT start_date FROM leagues WHERE league_id = p_league_id)
            AND report_date <= (SELECT end_date FROM leagues WHERE league_id = p_league_id)
        ), 0),
        accuracy = COALESCE((
            SELECT CASE 
                WHEN SUM(total_questions) > 0 
                THEN (SUM(correct_answers)::DECIMAL / SUM(total_questions)::DECIMAL) * 100
                ELSE 0.0
            END
            FROM study_reports 
            WHERE user_id = league_participants.user_id 
            AND report_date >= (SELECT start_date FROM leagues WHERE league_id = p_league_id)
            AND report_date <= (SELECT end_date FROM leagues WHERE league_id = p_league_id)
        ), 0.0),
        streak = COALESCE((
            SELECT current_streak 
            FROM user_statistics 
            WHERE user_id = league_participants.user_id
        ), 0)
    WHERE league_id = p_league_id;
    
    -- Calculate points based on stats
    UPDATE league_participants 
    SET points = (
        study_time + -- 1 point per minute
        (tests_completed * 10) + -- 10 points per test
        (accuracy * 5) + -- 5 points per accuracy percentage
        (streak * 5) -- 5 points per streak day
    )
    WHERE league_id = p_league_id;
    
    -- Update rankings
    UPDATE league_participants 
    SET rank = ranked_participants.new_rank
    FROM (
        SELECT user_id, league_id,
               ROW_NUMBER() OVER (ORDER BY points DESC, study_time DESC, accuracy DESC) as new_rank
        FROM league_participants
        WHERE league_id = p_league_id
    ) ranked_participants
    WHERE league_participants.user_id = ranked_participants.user_id
    AND league_participants.league_id = ranked_participants.league_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to get league leaderboard
CREATE OR REPLACE FUNCTION get_league_leaderboard(p_league_id INTEGER, p_limit INTEGER DEFAULT 50)
RETURNS TABLE (
    rank INTEGER,
    user_id BIGINT,
    name VARCHAR(255),
    nickname VARCHAR(255),
    points INTEGER,
    study_time INTEGER,
    tests_completed INTEGER,
    accuracy DECIMAL(5,2),
    streak INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lp.rank,
        u.user_id,
        u.real_name,
        u.nickname,
        lp.points,
        lp.study_time,
        lp.tests_completed,
        lp.accuracy,
        lp.streak
    FROM league_participants lp
    JOIN users u ON lp.user_id = u.user_id
    WHERE lp.league_id = p_league_id
    ORDER BY lp.rank ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user's league position
CREATE OR REPLACE FUNCTION get_user_league_position(p_user_id BIGINT, p_league_id INTEGER)
RETURNS TABLE (
    rank INTEGER,
    points INTEGER,
    study_time INTEGER,
    tests_completed INTEGER,
    accuracy DECIMAL(5,2),
    streak INTEGER,
    total_participants BIGINT,
    percentile DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lp.rank,
        lp.points,
        lp.study_time,
        lp.tests_completed,
        lp.accuracy,
        lp.streak,
        COUNT(*) OVER() as total_participants,
        ROUND((1.0 - (lp.rank - 1.0) / COUNT(*) OVER()) * 100, 2) as percentile
    FROM league_participants lp
    WHERE lp.user_id = p_user_id AND lp.league_id = p_league_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to check if user can join league
CREATE OR REPLACE FUNCTION can_user_join_league(p_user_id BIGINT, p_league_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    league_record RECORD;
    user_points INTEGER;
    is_already_joined BOOLEAN;
BEGIN
    -- Get league info
    SELECT * INTO league_record FROM leagues WHERE league_id = p_league_id;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Check if league is active
    IF NOT league_record.is_active OR 
       league_record.start_date > CURRENT_DATE OR 
       league_record.end_date < CURRENT_DATE THEN
        RETURN FALSE;
    END IF;
    
    -- Check if league is full
    IF league_record.current_participants >= league_record.max_participants THEN
        RETURN FALSE;
    END IF;
    
    -- Check entry requirements
    IF (league_record.entry_requirements->>'entry_points')::INTEGER > 0 THEN
        SELECT total_points INTO user_points FROM user_levels WHERE user_id = p_user_id;
        IF user_points < (league_record.entry_requirements->>'entry_points')::INTEGER THEN
            RETURN FALSE;
        END IF;
    END IF;
    
    -- Check if user is already joined
    SELECT EXISTS(
        SELECT 1 FROM league_participants 
        WHERE user_id = p_user_id AND league_id = p_league_id
    ) INTO is_already_joined;
    
    IF is_already_joined THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate invite code for private league
CREATE OR REPLACE FUNCTION generate_invite_code()
RETURNS VARCHAR(20) AS $$
DECLARE
    code VARCHAR(20);
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Generate random 8-character code
        code := UPPER(substring(md5(random()::text) from 1 for 8));
        
        -- Check if code already exists
        SELECT EXISTS(
            SELECT 1 FROM private_leagues WHERE invite_code = code
        ) INTO code_exists;
        
        IF NOT code_exists THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Create view for active leagues dashboard
CREATE OR REPLACE VIEW active_leagues_dashboard AS
SELECT 
    l.league_id,
    l.name,
    l.tier,
    l.league_type,
    l.start_date,
    l.end_date,
    l.current_participants,
    l.max_participants,
    l.is_active,
    CASE 
        WHEN l.end_date < CURRENT_DATE THEN 'ended'
        WHEN l.start_date > CURRENT_DATE THEN 'upcoming'
        ELSE 'active'
    END as status
FROM leagues l
WHERE l.is_active = TRUE
ORDER BY l.start_date DESC;

-- Insert default leagues for current period
INSERT INTO leagues (name, tier, league_type, start_date, end_date, max_participants, entry_requirements, rewards) VALUES
('Daily League - 2025-10-20', 'bronze', 'daily', CURRENT_DATE, CURRENT_DATE, 100, '{"entry_points": 0}', '{"top_1": {"points": 100, "badge": "daily_champion"}, "top_3": {"points": 50, "badge": "daily_top3"}, "top_10": {"points": 25, "badge": "daily_top10"}}'),
('Weekly League - Week 43', 'silver', 'weekly', CURRENT_DATE, CURRENT_DATE + INTERVAL '6 days', 500, '{"entry_points": 100}', '{"top_1": {"points": 500, "badge": "weekly_champion"}, "top_3": {"points": 300, "badge": "weekly_top3"}, "top_10": {"points": 150, "badge": "weekly_top10"}}'),
('Monthly League - October 2025', 'gold', 'monthly', CURRENT_DATE, CURRENT_DATE + INTERVAL '29 days', 1000, '{"entry_points": 500}', '{"top_1": {"points": 2000, "badge": "monthly_champion"}, "top_3": {"points": 1200, "badge": "monthly_top3"}, "top_10": {"points": 600, "badge": "monthly_top10"}}');

COMMENT ON TABLE leagues IS 'League competitions and tournaments';
COMMENT ON TABLE league_participants IS 'Users participating in leagues';
COMMENT ON TABLE league_rewards_log IS 'Log of distributed league rewards';
COMMENT ON TABLE user_rewards IS 'User rewards and prizes';
COMMENT ON TABLE private_leagues IS 'Private leagues created by users';
COMMENT ON TABLE private_league_participants IS 'Participants in private leagues';
COMMENT ON TABLE league_challenges IS 'Special challenges within leagues';
COMMENT ON TABLE user_challenge_progress IS 'User progress in league challenges';
