-- SarlakBot v3.2.0 - AI Coach System Database Schema
-- Migration: 008_ai_coach_system_tables.sql
-- Date: 2025-01-21
-- Description: AI Coach & Advanced Analytics System tables

-- ===========================================================
-- 🤖 AI COACH SYSTEM TABLES
-- ===========================================================

-- Study Analytics Table
CREATE TABLE IF NOT EXISTS study_analytics (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_study_time INTEGER DEFAULT 0, -- in minutes
    effective_study_time INTEGER DEFAULT 0, -- in minutes
    study_sessions INTEGER DEFAULT 0,
    subjects_studied TEXT[], -- array of subjects
    difficulty_levels JSONB, -- difficulty analysis per subject
    performance_scores JSONB, -- performance scores per subject
    study_patterns JSONB, -- detected study patterns
    efficiency_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    focus_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    consistency_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI Recommendations Table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL, -- 'study_plan', 'subject_priority', 'break_schedule', 'goal_task'
    recommendation_data JSONB NOT NULL, -- recommendation details
    priority_level INTEGER DEFAULT 1, -- 1-5 priority
    is_active BOOLEAN DEFAULT TRUE,
    is_accepted BOOLEAN DEFAULT FALSE,
    acceptance_date TIMESTAMP,
    effectiveness_score DECIMAL(5,2), -- 0-100
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Learning Paths Table
CREATE TABLE IF NOT EXISTS learning_paths (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    path_name VARCHAR(100) NOT NULL,
    path_description TEXT,
    subjects_sequence JSONB NOT NULL, -- ordered list of subjects
    difficulty_progression JSONB, -- difficulty progression
    estimated_duration INTEGER, -- in days
    current_position INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Study Schedules Table
CREATE TABLE IF NOT EXISTS study_schedules (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    schedule_date DATE NOT NULL,
    time_slots JSONB NOT NULL, -- array of time slots with subjects
    total_planned_time INTEGER DEFAULT 0, -- in minutes
    total_actual_time INTEGER DEFAULT 0, -- in minutes
    completion_rate DECIMAL(5,2) DEFAULT 0.0,
    is_optimized BOOLEAN DEFAULT FALSE,
    optimization_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance Predictions Table
CREATE TABLE IF NOT EXISTS performance_predictions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    prediction_type VARCHAR(50) NOT NULL, -- 'exam_score', 'improvement_timeline', 'success_probability'
    subject VARCHAR(100),
    predicted_value DECIMAL(5,2), -- predicted score/percentage
    confidence_level DECIMAL(5,2), -- 0-100 confidence
    prediction_data JSONB, -- detailed prediction data
    actual_value DECIMAL(5,2), -- actual result when available
    accuracy_score DECIMAL(5,2), -- prediction accuracy
    prediction_date TIMESTAMP DEFAULT NOW(),
    target_date DATE, -- when prediction should be evaluated
    is_achieved BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Learning Patterns Table
CREATE TABLE IF NOT EXISTS user_learning_patterns (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL, -- 'study_time', 'subject_preference', 'difficulty_progression'
    pattern_data JSONB NOT NULL, -- pattern details
    confidence_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Coach Interactions Table
CREATE TABLE IF NOT EXISTS ai_coach_interactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'recommendation', 'encouragement', 'warning', 'celebration'
    message_content TEXT NOT NULL,
    context_data JSONB, -- context of the interaction
    user_response VARCHAR(20), -- 'accepted', 'rejected', 'ignored'
    effectiveness_rating INTEGER, -- 1-5 user rating
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================================================
-- 📊 INDEXES FOR PERFORMANCE
-- ===========================================================

-- Study Analytics indexes
CREATE INDEX IF NOT EXISTS idx_study_analytics_user_date ON study_analytics(user_id, analysis_date);
CREATE INDEX IF NOT EXISTS idx_study_analytics_efficiency ON study_analytics(efficiency_score);
CREATE INDEX IF NOT EXISTS idx_study_analytics_created ON study_analytics(created_at);

-- AI Recommendations indexes
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_user ON ai_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_type ON ai_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_active ON ai_recommendations(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_priority ON ai_recommendations(priority_level);

-- Learning Paths indexes
CREATE INDEX IF NOT EXISTS idx_learning_paths_user ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_active ON learning_paths(is_active);
CREATE INDEX IF NOT EXISTS idx_learning_paths_completion ON learning_paths(completion_percentage);

-- Study Schedules indexes
CREATE INDEX IF NOT EXISTS idx_study_schedules_user_date ON study_schedules(user_id, schedule_date);
CREATE INDEX IF NOT EXISTS idx_study_schedules_optimized ON study_schedules(is_optimized);

-- Performance Predictions indexes
CREATE INDEX IF NOT EXISTS idx_performance_predictions_user ON performance_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_type ON performance_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_target ON performance_predictions(target_date);

-- User Learning Patterns indexes
CREATE INDEX IF NOT EXISTS idx_user_learning_patterns_user ON user_learning_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_user_learning_patterns_type ON user_learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_user_learning_patterns_active ON user_learning_patterns(is_active);

-- AI Coach Interactions indexes
CREATE INDEX IF NOT EXISTS idx_ai_coach_interactions_user ON ai_coach_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_coach_interactions_type ON ai_coach_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_ai_coach_interactions_created ON ai_coach_interactions(created_at);

-- ===========================================================
-- 🔧 TRIGGERS FOR AUTOMATIC UPDATES
-- ===========================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at column
CREATE TRIGGER update_study_analytics_updated_at
    BEFORE UPDATE ON study_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_paths_updated_at
    BEFORE UPDATE ON learning_paths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_schedules_updated_at
    BEFORE UPDATE ON study_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===========================================================
-- 📊 VIEWS FOR COMMON QUERIES
-- ===========================================================

-- User Analytics Summary View
CREATE OR REPLACE VIEW user_analytics_summary AS
SELECT
    u.user_id,
    u.real_name,
    u.nickname,
    sa.total_study_time,
    sa.effective_study_time,
    sa.efficiency_score,
    sa.focus_score,
    sa.consistency_score,
    sa.analysis_date,
    COUNT(ar.id) as active_recommendations,
    COUNT(lp.id) as active_learning_paths,
    COUNT(pp.id) as pending_predictions
FROM users u
LEFT JOIN study_analytics sa ON u.user_id = sa.user_id
LEFT JOIN ai_recommendations ar ON u.user_id = ar.user_id AND ar.is_active = TRUE
LEFT JOIN learning_paths lp ON u.user_id = lp.user_id AND lp.is_active = TRUE
LEFT JOIN performance_predictions pp ON u.user_id = pp.user_id AND pp.target_date > CURRENT_DATE
GROUP BY u.user_id, u.real_name, u.nickname, sa.total_study_time, sa.effective_study_time,
         sa.efficiency_score, sa.focus_score, sa.consistency_score, sa.analysis_date;

-- AI Coach Performance View
CREATE OR REPLACE VIEW ai_coach_performance AS
SELECT
    DATE(aci.created_at) as interaction_date,
    aci.interaction_type,
    COUNT(*) as total_interactions,
    COUNT(CASE WHEN aci.user_response = 'accepted' THEN 1 END) as accepted_count,
    COUNT(CASE WHEN aci.user_response = 'rejected' THEN 1 END) as rejected_count,
    AVG(aci.effectiveness_rating) as avg_effectiveness_rating
FROM ai_coach_interactions aci
WHERE aci.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(aci.created_at), aci.interaction_type
ORDER BY interaction_date DESC;

-- ===========================================================
-- 🎯 SAMPLE DATA FOR TESTING
-- ===========================================================

-- Insert sample analytics data for existing users
INSERT INTO study_analytics (user_id, total_study_time, effective_study_time, study_sessions,
                           subjects_studied, efficiency_score, focus_score, consistency_score)
SELECT
    u.user_id,
    FLOOR(RANDOM() * 300) + 60, -- 60-360 minutes
    FLOOR(RANDOM() * 250) + 50, -- 50-300 minutes
    FLOOR(RANDOM() * 10) + 1,   -- 1-10 sessions
    ARRAY['ریاضی', 'فیزیک', 'شیمی'],
    ROUND((RANDOM() * 40) + 60, 2), -- 60-100 efficiency
    ROUND((RANDOM() * 30) + 70, 2), -- 70-100 focus
    ROUND((RANDOM() * 25) + 75, 2)  -- 75-100 consistency
FROM users u
WHERE u.onboarding_completed = TRUE
ON CONFLICT DO NOTHING;

-- Insert sample AI recommendations
INSERT INTO ai_recommendations (user_id, recommendation_type, recommendation_data, priority_level)
SELECT
    u.user_id,
    'study_plan',
    '{"subjects": ["ریاضی", "فیزیک"], "duration": 120, "difficulty": "medium"}',
    FLOOR(RANDOM() * 3) + 1
FROM users u
WHERE u.onboarding_completed = TRUE
LIMIT 10
ON CONFLICT DO NOTHING;

-- ===========================================================
-- ✅ MIGRATION COMPLETE
-- ===========================================================

-- Log migration completion
INSERT INTO migration_log (migration_name, applied_at, description)
VALUES (
    '008_ai_coach_system_tables',
    NOW(),
    'AI Coach & Advanced Analytics System tables created successfully'
) ON CONFLICT DO NOTHING;
