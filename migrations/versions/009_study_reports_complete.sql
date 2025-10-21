-- Migration: Complete Study Reports System
-- Version: 009
-- Date: 2025-10-20
-- Description: Complete study reports and tracking system

-- Create study_reports table if not exists
CREATE TABLE IF NOT EXISTS study_reports (
    report_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    report_date DATE NOT NULL DEFAULT CURRENT_DATE,
    study_minutes INTEGER DEFAULT 0,
    tests_count INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    subjects_studied TEXT[] DEFAULT '{}',
    study_sessions INTEGER DEFAULT 0,
    break_time_minutes INTEGER DEFAULT 0,
    focus_score DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, report_date)
);

-- Create study_sessions table for detailed tracking
CREATE TABLE IF NOT EXISTS study_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER DEFAULT 0,
    subject VARCHAR(100),
    session_type VARCHAR(50) DEFAULT 'study', -- study, test, review
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create test_sessions table for test tracking
CREATE TABLE IF NOT EXISTS test_sessions (
    test_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    test_date DATE NOT NULL DEFAULT CURRENT_DATE,
    test_type VARCHAR(100) NOT NULL, -- mock, practice, official
    subject VARCHAR(100) NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    score DECIMAL(5,2),
    time_taken_minutes INTEGER,
    difficulty_level VARCHAR(50),
    test_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create study_goals table for goal tracking
CREATE TABLE IF NOT EXISTS study_goals (
    goal_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly
    goal_target INTEGER NOT NULL, -- minutes, questions, etc.
    goal_unit VARCHAR(20) NOT NULL, -- minutes, questions, tests
    goal_period_start DATE NOT NULL,
    goal_period_end DATE NOT NULL,
    current_progress INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_study_reports_user_date ON study_reports(user_id, report_date);
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_date ON study_sessions(user_id, session_date);
CREATE INDEX IF NOT EXISTS idx_test_sessions_user_date ON test_sessions(user_id, test_date);
CREATE INDEX IF NOT EXISTS idx_study_goals_user_type ON study_goals(user_id, goal_type);

-- Create function to update study reports
CREATE OR REPLACE FUNCTION update_study_report(
    p_user_id BIGINT,
    p_report_date DATE DEFAULT CURRENT_DATE,
    p_study_minutes INTEGER DEFAULT 0,
    p_tests_count INTEGER DEFAULT 0,
    p_correct_answers INTEGER DEFAULT 0,
    p_total_questions INTEGER DEFAULT 0,
    p_subjects_studied TEXT[] DEFAULT '{}',
    p_study_sessions INTEGER DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    INSERT INTO study_reports (
        user_id, report_date, study_minutes, tests_count, 
        correct_answers, total_questions, subjects_studied, study_sessions
    ) VALUES (
        p_user_id, p_report_date, p_study_minutes, p_tests_count,
        p_correct_answers, p_total_questions, p_subjects_studied, p_study_sessions
    )
    ON CONFLICT (user_id, report_date)
    DO UPDATE SET
        study_minutes = study_reports.study_minutes + p_study_minutes,
        tests_count = study_reports.tests_count + p_tests_count,
        correct_answers = study_reports.correct_answers + p_correct_answers,
        total_questions = study_reports.total_questions + p_total_questions,
        subjects_studied = ARRAY(
            SELECT DISTINCT unnest(study_reports.subjects_studied || p_subjects_studied)
        ),
        study_sessions = study_reports.study_sessions + p_study_sessions,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Create function to get study statistics
CREATE OR REPLACE FUNCTION get_study_statistics(p_user_id BIGINT, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    total_study_minutes BIGINT,
    total_tests INTEGER,
    total_questions INTEGER,
    correct_answers INTEGER,
    accuracy_rate DECIMAL,
    average_session_minutes DECIMAL,
    study_days INTEGER,
    current_streak INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(sr.study_minutes), 0)::BIGINT as total_study_minutes,
        COALESCE(SUM(sr.tests_count), 0)::INTEGER as total_tests,
        COALESCE(SUM(sr.total_questions), 0)::INTEGER as total_questions,
        COALESCE(SUM(sr.correct_answers), 0)::INTEGER as correct_answers,
        CASE 
            WHEN SUM(sr.total_questions) > 0 
            THEN ROUND((SUM(sr.correct_answers)::DECIMAL / SUM(sr.total_questions)::DECIMAL) * 100, 2)
            ELSE 0.00
        END as accuracy_rate,
        CASE 
            WHEN SUM(sr.study_sessions) > 0 
            THEN ROUND(SUM(sr.study_minutes)::DECIMAL / SUM(sr.study_sessions)::DECIMAL, 2)
            ELSE 0.00
        END as average_session_minutes,
        COUNT(DISTINCT sr.report_date)::INTEGER as study_days,
        (
            SELECT COUNT(*)::INTEGER
            FROM (
                SELECT DISTINCT report_date
                FROM study_reports
                WHERE user_id = p_user_id 
                AND report_date <= CURRENT_DATE
                ORDER BY report_date DESC
                LIMIT 30
            ) recent_dates
            WHERE recent_dates.report_date = CURRENT_DATE - (ROW_NUMBER() OVER (ORDER BY report_date DESC) - 1)
        ) as current_streak
    FROM study_reports sr
    WHERE sr.user_id = p_user_id 
    AND sr.report_date >= CURRENT_DATE - INTERVAL '1 day' * p_days;
END;
$$ LANGUAGE plpgsql;

-- Create function to get daily progress
CREATE OR REPLACE FUNCTION get_daily_progress(p_user_id BIGINT, p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    report_date DATE,
    study_minutes INTEGER,
    tests_count INTEGER,
    correct_answers INTEGER,
    total_questions INTEGER,
    subjects_studied TEXT[],
    study_sessions INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.report_date,
        sr.study_minutes,
        sr.tests_count,
        sr.correct_answers,
        sr.total_questions,
        sr.subjects_studied,
        sr.study_sessions
    FROM study_reports sr
    WHERE sr.user_id = p_user_id 
    AND sr.report_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
    ORDER BY sr.report_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get subject statistics
CREATE OR REPLACE FUNCTION get_subject_statistics(p_user_id BIGINT, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    subject TEXT,
    study_minutes BIGINT,
    tests_count INTEGER,
    questions_answered INTEGER,
    correct_answers INTEGER,
    accuracy_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        subject_name as subject,
        COALESCE(SUM(sr.study_minutes), 0)::BIGINT as study_minutes,
        COALESCE(SUM(sr.tests_count), 0)::INTEGER as tests_count,
        COALESCE(SUM(sr.total_questions), 0)::INTEGER as questions_answered,
        COALESCE(SUM(sr.correct_answers), 0)::INTEGER as correct_answers,
        CASE 
            WHEN SUM(sr.total_questions) > 0 
            THEN ROUND((SUM(sr.correct_answers)::DECIMAL / SUM(sr.total_questions)::DECIMAL) * 100, 2)
            ELSE 0.00
        END as accuracy_rate
    FROM (
        SELECT unnest(subjects_studied) as subject_name, *
        FROM study_reports
        WHERE user_id = p_user_id 
        AND report_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
    ) sr
    GROUP BY subject_name
    ORDER BY study_minutes DESC;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing (optional)
-- INSERT INTO study_goals (user_id, goal_type, goal_target, goal_unit, goal_period_start, goal_period_end)
-- VALUES (694245594, 'daily', 120, 'minutes', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day');

COMMENT ON TABLE study_reports IS 'Daily study reports and statistics';
COMMENT ON TABLE study_sessions IS 'Detailed study session tracking';
COMMENT ON TABLE test_sessions IS 'Test and quiz session tracking';
COMMENT ON TABLE study_goals IS 'User study goals and targets';

COMMENT ON FUNCTION update_study_report IS 'Update or insert study report data';
COMMENT ON FUNCTION get_study_statistics IS 'Get comprehensive study statistics for a user';
COMMENT ON FUNCTION get_daily_progress IS 'Get daily progress data for charts';
COMMENT ON FUNCTION get_subject_statistics IS 'Get subject-wise statistics';
