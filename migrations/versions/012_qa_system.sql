-- Migration: Q&A System with OpenAI Integration
-- Version: 012
-- Date: 2025-10-20
-- Description: Complete Q&A system with OpenAI integration and points-based access

-- Create Q&A categories table
CREATE TABLE IF NOT EXISTS qa_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_description TEXT,
    category_icon VARCHAR(20) DEFAULT '❓',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Q&A questions table
CREATE TABLE IF NOT EXISTS qa_questions (
    question_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES qa_categories(category_id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_context TEXT, -- Additional context provided by user
    question_language VARCHAR(10) DEFAULT 'fa',
    points_cost INTEGER DEFAULT 10, -- Points required to ask this question
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, answered, failed
    priority VARCHAR(10) DEFAULT 'normal', -- low, normal, high, urgent
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create Q&A answers table
CREATE TABLE IF NOT EXISTS qa_answers (
    answer_id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES qa_questions(question_id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    answer_type VARCHAR(20) DEFAULT 'ai', -- ai, human, hybrid
    confidence_score DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    sources TEXT[], -- Array of source references
    follow_up_suggestions TEXT[], -- Suggested follow-up questions
    is_helpful BOOLEAN, -- User feedback
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Q&A sessions table
CREATE TABLE IF NOT EXISTS qa_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_title VARCHAR(255),
    total_questions INTEGER DEFAULT 0,
    total_points_spent INTEGER DEFAULT 0,
    session_status VARCHAR(20) DEFAULT 'active', -- active, completed, abandoned
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    last_activity TIMESTAMP DEFAULT NOW()
);

-- Create Q&A feedback table
CREATE TABLE IF NOT EXISTS qa_feedback (
    feedback_id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES qa_questions(question_id) ON DELETE CASCADE,
    answer_id INTEGER REFERENCES qa_answers(answer_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- 1-5 star rating
    feedback_text TEXT,
    is_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Q&A templates table
CREATE TABLE IF NOT EXISTS qa_templates (
    template_id SERIAL PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_description TEXT,
    template_prompt TEXT NOT NULL,
    category_id INTEGER REFERENCES qa_categories(category_id) ON DELETE SET NULL,
    points_cost INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Q&A usage analytics table
CREATE TABLE IF NOT EXISTS qa_analytics (
    analytics_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES qa_questions(question_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL, -- ask_question, view_answer, rate_answer, etc.
    points_spent INTEGER DEFAULT 0,
    session_duration INTEGER DEFAULT 0, -- in seconds
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user learning profiles table
CREATE TABLE IF NOT EXISTS user_learning_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    learning_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced, expert
    interest_areas TEXT[] DEFAULT '{}', -- Array of interest areas
    study_preferences JSONB DEFAULT '{}', -- Study preferences and patterns
    question_patterns JSONB DEFAULT '{}', -- Question asking patterns
    response_preferences JSONB DEFAULT '{}', -- Preferred response characteristics
    learning_goals TEXT[] DEFAULT '{}', -- User's learning goals
    strengths TEXT[] DEFAULT '{}', -- User's strengths
    weaknesses TEXT[] DEFAULT '{}', -- User's weaknesses
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create learning insights table
CREATE TABLE IF NOT EXISTS learning_insights (
    insight_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL, -- encouragement, diversity, goal_focus, etc.
    insight_data JSONB DEFAULT '{}', -- Insight details and metadata
    confidence_score DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_qa_questions_user ON qa_questions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_qa_questions_category ON qa_questions(category_id, status);
CREATE INDEX IF NOT EXISTS idx_qa_questions_status ON qa_questions(status, created_at);
CREATE INDEX IF NOT EXISTS idx_qa_answers_question ON qa_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_qa_sessions_user ON qa_sessions(user_id, started_at);
CREATE INDEX IF NOT EXISTS idx_qa_feedback_question ON qa_feedback(question_id, created_at);
CREATE INDEX IF NOT EXISTS idx_qa_analytics_user ON qa_analytics(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_user_learning_profiles_user ON user_learning_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_learning_profiles_level ON user_learning_profiles(learning_level);
CREATE INDEX IF NOT EXISTS idx_learning_insights_user ON learning_insights(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_learning_insights_type ON learning_insights(insight_type, is_read);

-- Create function to check if user has enough points for Q&A
CREATE OR REPLACE FUNCTION can_user_ask_question(p_user_id BIGINT, p_points_cost INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    user_points INTEGER;
BEGIN
    SELECT total_points INTO user_points 
    FROM user_levels 
    WHERE user_id = p_user_id;
    
    IF user_points IS NULL THEN
        user_points := 0;
    END IF;
    
    RETURN user_points >= p_points_cost;
END;
$$ LANGUAGE plpgsql;

-- Create function to deduct points for Q&A
CREATE OR REPLACE FUNCTION deduct_qa_points(p_user_id BIGINT, p_points INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE user_levels 
    SET total_points = total_points - p_points
    WHERE user_id = p_user_id AND total_points >= p_points;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Create function to get Q&A statistics
CREATE OR REPLACE FUNCTION get_qa_stats(p_user_id BIGINT, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    total_questions INTEGER,
    total_points_spent INTEGER,
    avg_rating DECIMAL(3,2),
    helpful_answers INTEGER,
    categories_used TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT q.question_id)::INTEGER as total_questions,
        COALESCE(SUM(q.points_cost), 0)::INTEGER as total_points_spent,
        COALESCE(AVG(f.rating), 0.0) as avg_rating,
        COUNT(CASE WHEN f.is_helpful = TRUE THEN 1 END)::INTEGER as helpful_answers,
        ARRAY_AGG(DISTINCT c.category_name) as categories_used
    FROM qa_questions q
    LEFT JOIN qa_feedback f ON q.question_id = f.question_id
    LEFT JOIN qa_categories c ON q.category_id = c.category_id
    WHERE q.user_id = p_user_id 
    AND q.created_at >= CURRENT_DATE - INTERVAL '1 day' * p_days;
END;
$$ LANGUAGE plpgsql;

-- Create function to get popular questions
CREATE OR REPLACE FUNCTION get_popular_questions(p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    question_id INTEGER,
    question_text TEXT,
    category_name VARCHAR(100),
    ask_count BIGINT,
    avg_rating DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.question_id,
        q.question_text,
        c.category_name,
        COUNT(*) as ask_count,
        COALESCE(AVG(f.rating), 0.0) as avg_rating
    FROM qa_questions q
    LEFT JOIN qa_categories c ON q.category_id = c.category_id
    LEFT JOIN qa_feedback f ON q.question_id = f.question_id
    WHERE q.status = 'answered'
    GROUP BY q.question_id, q.question_text, c.category_name
    ORDER BY ask_count DESC, avg_rating DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Insert default Q&A categories
INSERT INTO qa_categories (category_name, category_description, category_icon) VALUES
('ریاضی', 'سوالات مربوط به ریاضیات و محاسبات', '🔢'),
('فیزیک', 'سوالات فیزیک و علوم طبیعی', '⚡'),
('شیمی', 'سوالات شیمی و ترکیبات', '🧪'),
('زیست‌شناسی', 'سوالات زیست‌شناسی و علوم زیستی', '🧬'),
('ادبیات', 'سوالات ادبیات فارسی و زبان‌شناسی', '📚'),
('تاریخ', 'سوالات تاریخ ایران و جهان', '🏛️'),
('جغرافیا', 'سوالات جغرافیا و علوم زمین', '🌍'),
('زبان انگلیسی', 'سوالات زبان انگلیسی و گرامر', '🇬🇧'),
('دین و زندگی', 'سوالات دین و زندگی و اخلاق', '🕌'),
('روانشناسی', 'سوالات روانشناسی و علوم انسانی', '🧠'),
('مشاوره تحصیلی', 'راهنمایی و مشاوره تحصیلی', '🎓'),
('کنکور', 'سوالات عمومی کنکور و آمادگی', '📝'),
('انگیزشی', 'سوالات انگیزشی و روانشناسی', '💪'),
('عمومی', 'سوالات عمومی و متفرقه', '❓');

-- Insert default Q&A templates
INSERT INTO qa_templates (template_name, template_description, template_prompt, category_id, points_cost) VALUES
('سوال ریاضی', 'قالب استاندارد برای سوالات ریاضی', 'لطفاً این سوال ریاضی را حل کنید و مراحل حل را به صورت کامل توضیح دهید:', 1, 10),
('سوال فیزیک', 'قالب استاندارد برای سوالات فیزیک', 'این سوال فیزیک را با توضیح فرمول‌ها و محاسبات حل کنید:', 2, 10),
('سوال شیمی', 'قالب استاندارد برای سوالات شیمی', 'این سوال شیمی را با توضیح واکنش‌ها و محاسبات حل کنید:', 3, 10),
('مشاوره تحصیلی', 'قالب مشاوره تحصیلی', 'به عنوان مشاور تحصیلی، راهنمایی کاملی برای این موضوع ارائه دهید:', 11, 15),
('انگیزشی', 'قالب سوالات انگیزشی', 'به عنوان مربی انگیزشی، پاسخی الهام‌بخش و عملی برای این سوال ارائه دهید:', 13, 5);

-- Create view for Q&A dashboard
CREATE OR REPLACE VIEW qa_dashboard AS
SELECT 
    u.user_id,
    u.real_name,
    u.nickname,
    COALESCE(qa_stats.total_questions, 0) as total_questions,
    COALESCE(qa_stats.total_points_spent, 0) as total_points_spent,
    COALESCE(qa_stats.avg_rating, 0.0) as avg_rating,
    COALESCE(qa_stats.helpful_answers, 0) as helpful_answers,
    ul.total_points as current_points
FROM users u
LEFT JOIN user_levels ul ON u.user_id = ul.user_id
LEFT JOIN LATERAL get_qa_stats(u.user_id, 30) qa_stats ON TRUE
WHERE u.is_active = TRUE;

-- Create view for Q&A analytics
CREATE OR REPLACE VIEW qa_analytics_summary AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_questions,
    COUNT(CASE WHEN status = 'answered' THEN 1 END) as answered_questions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_questions,
    AVG(points_cost) as avg_points_cost,
    SUM(points_cost) as total_points_spent
FROM qa_questions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON TABLE qa_categories IS 'Q&A question categories';
COMMENT ON TABLE qa_questions IS 'User questions and their status';
COMMENT ON TABLE qa_answers IS 'AI-generated answers to questions';
COMMENT ON TABLE qa_sessions IS 'Q&A conversation sessions';
COMMENT ON TABLE qa_feedback IS 'User feedback on answers';
COMMENT ON TABLE qa_templates IS 'Predefined question templates';
COMMENT ON TABLE qa_analytics IS 'Q&A usage analytics';

COMMENT ON FUNCTION can_user_ask_question IS 'Check if user has enough points to ask a question';
COMMENT ON FUNCTION deduct_qa_points IS 'Deduct points for asking a question';
COMMENT ON FUNCTION get_qa_stats IS 'Get Q&A statistics for a user';
COMMENT ON FUNCTION get_popular_questions IS 'Get most popular questions';
