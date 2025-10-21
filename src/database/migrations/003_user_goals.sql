-- 🌌 SarlakBot v3.1.0 - User Goals Migration
-- Additive migration - safe to run multiple times

-- Create user_goals table for goal tracking
CREATE TABLE IF NOT EXISTS user_goals (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    daily_study_goal INTEGER,
    weekly_study_goal INTEGER,
    monthly_points_goal INTEGER,
    rank_goal INTEGER,
    subjects_goal VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_user_goals_daily_study ON user_goals(daily_study_goal);
CREATE INDEX IF NOT EXISTS idx_user_goals_weekly_study ON user_goals(weekly_study_goal);
CREATE INDEX IF NOT EXISTS idx_user_goals_monthly_points ON user_goals(monthly_points_goal);

-- Create function to get user goals
CREATE OR REPLACE FUNCTION get_user_goals(target_user_id BIGINT)
RETURNS TABLE(
    daily_study_goal INTEGER,
    weekly_study_goal INTEGER,
    monthly_points_goal INTEGER,
    rank_goal INTEGER,
    subjects_goal VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ug.daily_study_goal,
        ug.weekly_study_goal,
        ug.monthly_points_goal,
        ug.rank_goal,
        ug.subjects_goal
    FROM user_goals ug
    WHERE ug.user_id = target_user_id;
    
    -- If no goals found, return default values
    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::INTEGER, NULL::INTEGER, NULL::INTEGER, NULL::INTEGER, NULL::VARCHAR;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to update user goal
CREATE OR REPLACE FUNCTION update_user_goal(
    target_user_id BIGINT,
    goal_type VARCHAR(50),
    goal_value TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Insert or update goal
    IF goal_type = 'daily_study' THEN
        INSERT INTO user_goals (user_id, daily_study_goal, updated_at)
        VALUES (target_user_id, goal_value::INTEGER, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET daily_study_goal = goal_value::INTEGER, updated_at = NOW();
    ELSIF goal_type = 'weekly_study' THEN
        INSERT INTO user_goals (user_id, weekly_study_goal, updated_at)
        VALUES (target_user_id, goal_value::INTEGER, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET weekly_study_goal = goal_value::INTEGER, updated_at = NOW();
    ELSIF goal_type = 'monthly_points' THEN
        INSERT INTO user_goals (user_id, monthly_points_goal, updated_at)
        VALUES (target_user_id, goal_value::INTEGER, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET monthly_points_goal = goal_value::INTEGER, updated_at = NOW();
    ELSIF goal_type = 'rank' THEN
        INSERT INTO user_goals (user_id, rank_goal, updated_at)
        VALUES (target_user_id, goal_value::INTEGER, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET rank_goal = goal_value::INTEGER, updated_at = NOW();
    ELSIF goal_type = 'subjects' THEN
        INSERT INTO user_goals (user_id, subjects_goal, updated_at)
        VALUES (target_user_id, goal_value, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET subjects_goal = goal_value, updated_at = NOW();
    ELSE
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
