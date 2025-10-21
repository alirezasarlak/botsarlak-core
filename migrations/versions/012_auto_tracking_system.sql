-- Migration: Auto Tracking System
-- Version: 012
-- Date: 2025-10-20
-- Description: Complete automatic study tracking and reporting system

-- Create auto tracking sessions table
CREATE TABLE IF NOT EXISTS auto_tracking_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    tracking_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create auto tracked activities table
CREATE TABLE IF NOT EXISTS auto_tracked_activities (
    activity_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL, -- study_session, test_session, break_time, idle_time, focus_time, review_time
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL,
    subject VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user activities table (for raw activity data)
CREATE TABLE IF NOT EXISTS user_activities (
    activity_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    activity_data JSONB DEFAULT '{}',
    activity_time TIMESTAMP NOT NULL DEFAULT NOW(),
    device_info JSONB DEFAULT '{}',
    location_info JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create study patterns table
CREATE TABLE IF NOT EXISTS study_patterns (
    pattern_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL, -- daily, subject, time, duration, etc.
    pattern_data JSONB NOT NULL,
    frequency INTEGER DEFAULT 1,
    confidence DECIMAL(3,2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create smart notifications table
CREATE TABLE IF NOT EXISTS smart_notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL, -- achievement, goal, reminder, encouragement, etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_data JSONB DEFAULT '{}',
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create auto goals table
CREATE TABLE IF NOT EXISTS auto_goals (
    goal_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL, -- daily_study_time, weekly_sessions, monthly_accuracy, etc.
    current_target INTEGER NOT NULL,
    suggested_target INTEGER NOT NULL,
    adjustment_reason TEXT,
    is_applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create study insights table
CREATE TABLE IF NOT EXISTS study_insights (
    insight_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL, -- performance, pattern, recommendation, etc.
    insight_data JSONB NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.00,
    is_actionable BOOLEAN DEFAULT FALSE,
    action_taken BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_auto_tracking_sessions_user ON auto_tracking_sessions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_auto_tracked_activities_user_time ON auto_tracked_activities(user_id, start_time);
CREATE INDEX IF NOT EXISTS idx_auto_tracked_activities_type ON auto_tracked_activities(activity_type, start_time);
CREATE INDEX IF NOT EXISTS idx_user_activities_user_time ON user_activities(user_id, activity_time);
CREATE INDEX IF NOT EXISTS idx_study_patterns_user_type ON study_patterns(user_id, pattern_type);
CREATE INDEX IF NOT EXISTS idx_smart_notifications_user ON smart_notifications(user_id, is_sent);
CREATE INDEX IF NOT EXISTS idx_auto_goals_user ON auto_goals(user_id, is_applied);
CREATE INDEX IF NOT EXISTS idx_study_insights_user ON study_insights(user_id, created_at);

-- Create function to start auto tracking
CREATE OR REPLACE FUNCTION start_auto_tracking(p_user_id BIGINT)
RETURNS INTEGER AS $$
DECLARE
    session_id INTEGER;
BEGIN
    -- Check if user already has active tracking
    IF EXISTS(SELECT 1 FROM auto_tracking_sessions WHERE user_id = p_user_id AND is_active = TRUE) THEN
        RETURN -1; -- Already tracking
    END IF;
    
    -- Start new tracking session
    INSERT INTO auto_tracking_sessions (user_id, start_time, is_active)
    VALUES (p_user_id, NOW(), TRUE)
    RETURNING auto_tracking_sessions.session_id INTO session_id;
    
    RETURN session_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to stop auto tracking
CREATE OR REPLACE FUNCTION stop_auto_tracking(p_user_id BIGINT)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE auto_tracking_sessions 
    SET is_active = FALSE, end_time = NOW()
    WHERE user_id = p_user_id AND is_active = TRUE;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Create function to track activity
CREATE OR REPLACE FUNCTION track_activity(
    p_user_id BIGINT,
    p_activity_type VARCHAR(50),
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP,
    p_subject VARCHAR(100) DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}',
    p_confidence_score DECIMAL(3,2) DEFAULT 1.00
) RETURNS INTEGER AS $$
DECLARE
    activity_id INTEGER;
    duration_minutes INTEGER;
BEGIN
    duration_minutes := EXTRACT(EPOCH FROM (p_end_time - p_start_time)) / 60;
    
    INSERT INTO auto_tracked_activities 
    (user_id, activity_type, start_time, end_time, duration_minutes, subject, metadata, confidence_score)
    VALUES (p_user_id, p_activity_type, p_start_time, p_end_time, duration_minutes, p_subject, p_metadata, p_confidence_score)
    RETURNING auto_tracked_activities.activity_id INTO activity_id;
    
    -- Update study report
    IF p_activity_type = 'study_session' THEN
        PERFORM update_study_report(
            p_user_id, 
            CURRENT_DATE, 
            duration_minutes, 
            0, -- tests_count
            0, -- correct_answers
            0, -- total_questions
            CASE WHEN p_subject IS NOT NULL THEN ARRAY[p_subject] ELSE '{}' END, -- subjects_studied
            1 -- study_sessions
        );
    END IF;
    
    RETURN activity_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate auto report
CREATE OR REPLACE FUNCTION generate_auto_report(p_user_id BIGINT, p_date DATE DEFAULT CURRENT_DATE)
RETURNS JSONB AS $$
DECLARE
    report_data JSONB;
    total_study_time INTEGER;
    sessions_count INTEGER;
    subjects_studied TEXT[];
    focus_score DECIMAL(3,2);
    break_time INTEGER;
BEGIN
    -- Get study time
    SELECT COALESCE(SUM(duration_minutes), 0) INTO total_study_time
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND DATE(start_time) = p_date
    AND activity_type = 'study_session';
    
    -- Get sessions count
    SELECT COUNT(*) INTO sessions_count
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND DATE(start_time) = p_date
    AND activity_type = 'study_session';
    
    -- Get subjects studied
    SELECT ARRAY_AGG(DISTINCT subject) INTO subjects_studied
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND DATE(start_time) = p_date
    AND activity_type = 'study_session'
    AND subject IS NOT NULL;
    
    -- Calculate focus score
    SELECT COALESCE(AVG(duration_minutes), 0) / 60.0 INTO focus_score
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND DATE(start_time) = p_date
    AND activity_type = 'study_session';
    
    -- Get break time
    SELECT COALESCE(SUM(duration_minutes), 0) INTO break_time
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND DATE(start_time) = p_date
    AND activity_type = 'break_time';
    
    -- Build report data
    report_data := jsonb_build_object(
        'date', p_date,
        'total_study_time', total_study_time,
        'sessions_count', sessions_count,
        'subjects_studied', COALESCE(subjects_studied, '{}'),
        'focus_score', LEAST(focus_score, 1.0),
        'break_time', break_time,
        'generated_at', NOW()
    );
    
    RETURN report_data;
END;
$$ LANGUAGE plpgsql;

-- Create function to detect study sessions
CREATE OR REPLACE FUNCTION detect_study_sessions(p_user_id BIGINT, p_hours INTEGER DEFAULT 24)
RETURNS TABLE (
    session_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    subject VARCHAR(100),
    confidence DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        activity_id as session_id,
        start_time,
        end_time,
        duration_minutes,
        subject,
        confidence_score as confidence
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND start_time >= NOW() - INTERVAL '1 hour' * p_hours
    AND activity_type = 'study_session'
    AND duration_minutes >= 5
    ORDER BY start_time ASC;
END;
$$ LANGUAGE plpgsql;

-- Create function to analyze study patterns
CREATE OR REPLACE FUNCTION analyze_study_patterns(p_user_id BIGINT, p_days INTEGER DEFAULT 30)
RETURNS JSONB AS $$
DECLARE
    pattern_data JSONB;
    daily_avg DECIMAL(5,2);
    peak_hours INTEGER[];
    favorite_subjects TEXT[];
    avg_session_duration DECIMAL(5,2);
    study_consistency DECIMAL(3,2);
BEGIN
    -- Calculate daily average study time
    SELECT COALESCE(AVG(daily_total), 0) INTO daily_avg
    FROM (
        SELECT SUM(duration_minutes) as daily_total
        FROM auto_tracked_activities
        WHERE user_id = p_user_id 
        AND start_time >= NOW() - INTERVAL '1 day' * p_days
        AND activity_type = 'study_session'
        GROUP BY DATE(start_time)
    ) daily_totals;
    
    -- Find peak study hours
    SELECT ARRAY_AGG(hour ORDER BY study_count DESC LIMIT 3) INTO peak_hours
    FROM (
        SELECT EXTRACT(HOUR FROM start_time) as hour, COUNT(*) as study_count
        FROM auto_tracked_activities
        WHERE user_id = p_user_id 
        AND start_time >= NOW() - INTERVAL '1 day' * p_days
        AND activity_type = 'study_session'
        GROUP BY EXTRACT(HOUR FROM start_time)
    ) hour_stats;
    
    -- Find favorite subjects
    SELECT ARRAY_AGG(subject ORDER BY study_time DESC LIMIT 5) INTO favorite_subjects
    FROM (
        SELECT subject, SUM(duration_minutes) as study_time
        FROM auto_tracked_activities
        WHERE user_id = p_user_id 
        AND start_time >= NOW() - INTERVAL '1 day' * p_days
        AND activity_type = 'study_session'
        AND subject IS NOT NULL
        GROUP BY subject
    ) subject_stats;
    
    -- Calculate average session duration
    SELECT COALESCE(AVG(duration_minutes), 0) INTO avg_session_duration
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND start_time >= NOW() - INTERVAL '1 day' * p_days
    AND activity_type = 'study_session';
    
    -- Calculate study consistency (days with study / total days)
    SELECT COALESCE(
        COUNT(DISTINCT DATE(start_time))::DECIMAL / p_days, 0
    ) INTO study_consistency
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND start_time >= NOW() - INTERVAL '1 day' * p_days
    AND activity_type = 'study_session';
    
    -- Build pattern data
    pattern_data := jsonb_build_object(
        'daily_average_minutes', daily_avg,
        'peak_hours', COALESCE(peak_hours, '{}'),
        'favorite_subjects', COALESCE(favorite_subjects, '{}'),
        'avg_session_duration', avg_session_duration,
        'study_consistency', study_consistency,
        'analysis_period_days', p_days,
        'analyzed_at', NOW()
    );
    
    RETURN pattern_data;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate smart recommendations
CREATE OR REPLACE FUNCTION generate_smart_recommendations(p_user_id BIGINT)
RETURNS TEXT[] AS $$
DECLARE
    recommendations TEXT[] := '{}';
    daily_avg DECIMAL(5,2);
    study_consistency DECIMAL(3,2);
    recent_study_time INTEGER;
    pattern_data JSONB;
BEGIN
    -- Get recent study data
    SELECT COALESCE(SUM(duration_minutes), 0) INTO recent_study_time
    FROM auto_tracked_activities
    WHERE user_id = p_user_id 
    AND start_time >= NOW() - INTERVAL '7 days'
    AND activity_type = 'study_session';
    
    -- Get pattern analysis
    SELECT analyze_study_patterns(p_user_id, 30) INTO pattern_data;
    daily_avg := (pattern_data->>'daily_average_minutes')::DECIMAL;
    study_consistency := (pattern_data->>'study_consistency')::DECIMAL;
    
    -- Generate recommendations based on data
    IF recent_study_time = 0 THEN
        recommendations := array_append(recommendations, 'شروع به مطالعه کنید تا پیشرفت خود را پیگیری کنید!');
    ELSIF recent_study_time < 60 THEN
        recommendations := array_append(recommendations, 'زمان مطالعه خود را افزایش دهید. هدف روزانه 120 دقیقه است.');
    ELSIF recent_study_time > 300 THEN
        recommendations := array_append(recommendations, 'زمان مطالعه عالی! مراقب خستگی باشید.');
    END IF;
    
    IF study_consistency < 0.5 THEN
        recommendations := array_append(recommendations, 'مطالعه منظم داشته باشید. حتی 30 دقیقه در روز مفید است.');
    ELSIF study_consistency > 0.8 THEN
        recommendations := array_append(recommendations, 'مطالعه منظم عالی! این عادت را حفظ کنید.');
    END IF;
    
    IF daily_avg < 60 THEN
        recommendations := array_append(recommendations, 'هدف روزانه 120 دقیقه مطالعه را در نظر بگیرید.');
    ELSIF daily_avg > 180 THEN
        recommendations := array_append(recommendations, 'زمان مطالعه زیاد است. کیفیت مهم‌تر از کمیت است.');
    END IF;
    
    RETURN recommendations;
END;
$$ LANGUAGE plpgsql;

-- Create function to create smart notification
CREATE OR REPLACE FUNCTION create_smart_notification(
    p_user_id BIGINT,
    p_notification_type VARCHAR(50),
    p_title VARCHAR(255),
    p_message TEXT,
    p_data JSONB DEFAULT '{}'
) RETURNS INTEGER AS $$
DECLARE
    notification_id INTEGER;
BEGIN
    INSERT INTO smart_notifications 
    (user_id, notification_type, title, message, notification_data)
    VALUES (p_user_id, p_notification_type, p_title, p_message, p_data)
    RETURNING smart_notifications.notification_id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Create view for auto tracking dashboard
CREATE OR REPLACE VIEW auto_tracking_dashboard AS
SELECT 
    u.user_id,
    u.real_name,
    u.nickname,
    ats.session_id,
    ats.start_time as tracking_start,
    ats.is_active,
    COALESCE(daily_stats.total_study_time, 0) as today_study_time,
    COALESCE(daily_stats.sessions_count, 0) as today_sessions,
    COALESCE(weekly_stats.total_study_time, 0) as week_study_time,
    COALESCE(weekly_stats.sessions_count, 0) as week_sessions
FROM users u
LEFT JOIN auto_tracking_sessions ats ON u.user_id = ats.user_id AND ats.is_active = TRUE
LEFT JOIN (
    SELECT 
        user_id,
        SUM(duration_minutes) as total_study_time,
        COUNT(*) as sessions_count
    FROM auto_tracked_activities
    WHERE DATE(start_time) = CURRENT_DATE
    AND activity_type = 'study_session'
    GROUP BY user_id
) daily_stats ON u.user_id = daily_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        SUM(duration_minutes) as total_study_time,
        COUNT(*) as sessions_count
    FROM auto_tracked_activities
    WHERE start_time >= CURRENT_DATE - INTERVAL '7 days'
    AND activity_type = 'study_session'
    GROUP BY user_id
) weekly_stats ON u.user_id = weekly_stats.user_id;

COMMENT ON TABLE auto_tracking_sessions IS 'Active auto tracking sessions for users';
COMMENT ON TABLE auto_tracked_activities IS 'Automatically tracked study activities';
COMMENT ON TABLE user_activities IS 'Raw user activity data for analysis';
COMMENT ON TABLE study_patterns IS 'Analyzed study patterns for users';
COMMENT ON TABLE smart_notifications IS 'Smart notifications for users';
COMMENT ON TABLE auto_goals IS 'Automatically adjusted study goals';
COMMENT ON TABLE study_insights IS 'AI-generated study insights';

COMMENT ON FUNCTION start_auto_tracking IS 'Start automatic tracking for a user';
COMMENT ON FUNCTION stop_auto_tracking IS 'Stop automatic tracking for a user';
COMMENT ON FUNCTION track_activity IS 'Track a specific activity';
COMMENT ON FUNCTION generate_auto_report IS 'Generate automatic study report';
COMMENT ON FUNCTION detect_study_sessions IS 'Detect study sessions from activity data';
COMMENT ON FUNCTION analyze_study_patterns IS 'Analyze user study patterns';
COMMENT ON FUNCTION generate_smart_recommendations IS 'Generate smart study recommendations';
COMMENT ON FUNCTION create_smart_notification IS 'Create a smart notification for user';
