-- Migration: Anti-Fraud System
-- Version: 010
-- Date: 2025-10-20
-- Description: Complete anti-fraud and cheating detection system

-- Create fraud detection logs table
CREATE TABLE IF NOT EXISTS fraud_detection_logs (
    log_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    is_fraud BOOLEAN NOT NULL DEFAULT FALSE,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low', -- low, medium, high, critical
    reasons TEXT[] DEFAULT '{}',
    confidence DECIMAL(3,2) DEFAULT 0.00,
    actions_taken TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create suspicious sessions table
CREATE TABLE IF NOT EXISTS suspicious_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    fraud_result TEXT[] DEFAULT '{}',
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
    session_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user restrictions table
CREATE TABLE IF NOT EXISTS user_restrictions (
    restriction_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    restriction_type VARCHAR(50) NOT NULL, -- study_limit, report_limit, etc.
    reason TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create device fingerprints table
CREATE TABLE IF NOT EXISTS device_fingerprints (
    fingerprint_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_fingerprint VARCHAR(255) NOT NULL,
    device_info JSONB DEFAULT '{}',
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    is_trusted BOOLEAN DEFAULT FALSE
);

-- Create study session validation table
CREATE TABLE IF NOT EXISTS study_session_validations (
    validation_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES study_sessions(session_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    validation_result JSONB DEFAULT '{}',
    fraud_score DECIMAL(3,2) DEFAULT 0.00,
    is_valid BOOLEAN DEFAULT TRUE,
    validation_timestamp TIMESTAMP DEFAULT NOW()
);

-- Create fraud patterns table
CREATE TABLE IF NOT EXISTS fraud_patterns (
    pattern_id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_description TEXT,
    detection_rules JSONB DEFAULT '{}',
    severity_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fraud_logs_user_date ON fraud_detection_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_risk_level ON fraud_detection_logs(risk_level, created_at);
CREATE INDEX IF NOT EXISTS idx_suspicious_sessions_user_date ON suspicious_sessions(user_id, session_date);
CREATE INDEX IF NOT EXISTS idx_user_restrictions_user_expires ON user_restrictions(user_id, expires_at);
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_user ON device_fingerprints(user_id, last_seen);
CREATE INDEX IF NOT EXISTS idx_session_validations_user ON study_session_validations(user_id, validation_timestamp);

-- Create function to detect fraud patterns
CREATE OR REPLACE FUNCTION detect_fraud_patterns(p_user_id BIGINT, p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    pattern_name VARCHAR(100),
    pattern_count INTEGER,
    risk_score DECIMAL(3,2),
    last_occurrence TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'rapid_sessions'::VARCHAR(100) as pattern_name,
        COUNT(*)::INTEGER as pattern_count,
        CASE 
            WHEN COUNT(*) > 10 THEN 0.9
            WHEN COUNT(*) > 5 THEN 0.6
            ELSE 0.3
        END as risk_score,
        MAX(created_at) as last_occurrence
    FROM study_sessions ss
    WHERE ss.user_id = p_user_id 
    AND ss.session_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
    GROUP BY ss.user_id
    HAVING COUNT(*) > 3
    
    UNION ALL
    
    SELECT 
        'perfect_accuracy'::VARCHAR(100) as pattern_name,
        COUNT(*)::INTEGER as pattern_count,
        CASE 
            WHEN COUNT(*) > 5 THEN 0.8
            WHEN COUNT(*) > 2 THEN 0.5
            ELSE 0.2
        END as risk_score,
        MAX(created_at) as last_occurrence
    FROM study_reports sr
    WHERE sr.user_id = p_user_id 
    AND sr.report_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
    AND sr.total_questions > 0
    AND (sr.correct_answers::DECIMAL / sr.total_questions::DECIMAL) = 1.0
    GROUP BY sr.user_id
    HAVING COUNT(*) > 1;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user fraud score
CREATE OR REPLACE FUNCTION get_user_fraud_score(p_user_id BIGINT, p_days INTEGER DEFAULT 30)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    fraud_count INTEGER;
    total_sessions INTEGER;
    fraud_score DECIMAL(3,2);
BEGIN
    -- Count fraud detections
    SELECT COUNT(*) INTO fraud_count
    FROM fraud_detection_logs
    WHERE user_id = p_user_id 
    AND created_at >= CURRENT_DATE - INTERVAL '1 day' * p_days
    AND is_fraud = TRUE;
    
    -- Count total sessions
    SELECT COUNT(*) INTO total_sessions
    FROM study_sessions
    WHERE user_id = p_user_id 
    AND session_date >= CURRENT_DATE - INTERVAL '1 day' * p_days;
    
    -- Calculate fraud score
    IF total_sessions = 0 THEN
        fraud_score := 0.0;
    ELSE
        fraud_score := (fraud_count::DECIMAL / total_sessions::DECIMAL) * 100;
    END IF;
    
    RETURN LEAST(fraud_score, 100.0);
END;
$$ LANGUAGE plpgsql;

-- Create function to check if user is restricted
CREATE OR REPLACE FUNCTION is_user_restricted(p_user_id BIGINT)
RETURNS BOOLEAN AS $$
DECLARE
    restriction_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO restriction_count
    FROM user_restrictions
    WHERE user_id = p_user_id 
    AND expires_at > NOW();
    
    RETURN restriction_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Create function to log fraud detection
CREATE OR REPLACE FUNCTION log_fraud_detection(
    p_user_id BIGINT,
    p_is_fraud BOOLEAN,
    p_risk_level VARCHAR(20),
    p_reasons TEXT[],
    p_confidence DECIMAL(3,2),
    p_actions_taken TEXT[],
    p_metadata JSONB DEFAULT '{}'
) RETURNS INTEGER AS $$
DECLARE
    log_id INTEGER;
BEGIN
    INSERT INTO fraud_detection_logs (
        user_id, is_fraud, risk_level, reasons, confidence, actions_taken, metadata
    ) VALUES (
        p_user_id, p_is_fraud, p_risk_level, p_reasons, p_confidence, p_actions_taken, p_metadata
    ) RETURNING fraud_detection_logs.log_id INTO log_id;
    
    RETURN log_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to add user restriction
CREATE OR REPLACE FUNCTION add_user_restriction(
    p_user_id BIGINT,
    p_restriction_type VARCHAR(50),
    p_reason TEXT,
    p_duration_hours INTEGER DEFAULT 24
) RETURNS INTEGER AS $$
DECLARE
    restriction_id INTEGER;
BEGIN
    INSERT INTO user_restrictions (
        user_id, restriction_type, reason, expires_at
    ) VALUES (
        p_user_id, p_restriction_type, p_reason, NOW() + INTERVAL '1 hour' * p_duration_hours
    ) RETURNING user_restrictions.restriction_id INTO restriction_id;
    
    RETURN restriction_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to validate study session
CREATE OR REPLACE FUNCTION validate_study_session(
    p_user_id BIGINT,
    p_duration_minutes INTEGER,
    p_questions_answered INTEGER DEFAULT 0,
    p_correct_answers INTEGER DEFAULT 0,
    p_device_fingerprint VARCHAR(255) DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
    validation_result JSONB;
    fraud_score DECIMAL(3,2);
    is_valid BOOLEAN;
    reasons TEXT[] DEFAULT '{}';
BEGIN
    -- Initialize validation result
    validation_result := '{"is_valid": true, "fraud_score": 0.0, "reasons": []}'::JSONB;
    
    -- Check if user is restricted
    IF is_user_restricted(p_user_id) THEN
        validation_result := jsonb_set(validation_result, '{is_valid}', 'false');
        validation_result := jsonb_set(validation_result, '{fraud_score}', '100.0');
        validation_result := jsonb_set(validation_result, '{reasons}', '["User is currently restricted"]');
        RETURN validation_result;
    END IF;
    
    -- Basic validation checks
    IF p_duration_minutes > 480 THEN -- 8 hours
        reasons := array_append(reasons, 'Session duration exceeds daily limit');
    END IF;
    
    IF p_duration_minutes < 5 THEN
        reasons := array_append(reasons, 'Session duration too short');
    END IF;
    
    IF p_questions_answered > 0 AND p_duration_minutes > 0 THEN
        IF (p_questions_answered::DECIMAL / p_duration_minutes::DECIMAL) > 10 THEN
            reasons := array_append(reasons, 'Answering speed too high');
        END IF;
    END IF;
    
    IF p_questions_answered > 0 THEN
        IF (p_correct_answers::DECIMAL / p_questions_answered::DECIMAL) > 0.95 THEN
            reasons := array_append(reasons, 'Accuracy suspiciously high');
        END IF;
    END IF;
    
    -- Calculate fraud score
    fraud_score := array_length(reasons, 1) * 20.0;
    IF fraud_score > 100.0 THEN
        fraud_score := 100.0;
    END IF;
    
    -- Determine if session is valid
    is_valid := fraud_score < 60.0;
    
    -- Update validation result
    validation_result := jsonb_set(validation_result, '{is_valid}', to_jsonb(is_valid));
    validation_result := jsonb_set(validation_result, '{fraud_score}', to_jsonb(fraud_score));
    validation_result := jsonb_set(validation_result, '{reasons}', to_jsonb(reasons));
    
    RETURN validation_result;
END;
$$ LANGUAGE plpgsql;

-- Insert default fraud patterns
INSERT INTO fraud_patterns (pattern_name, pattern_description, detection_rules, severity_level) VALUES
('rapid_sessions', 'Multiple study sessions in short time periods', '{"max_sessions_per_hour": 3, "min_break_time": 300}', 'medium'),
('perfect_accuracy', 'Consistently perfect test scores', '{"min_questions": 10, "accuracy_threshold": 0.95}', 'high'),
('excessive_study_time', 'Study time exceeds realistic limits', '{"max_daily_hours": 8, "max_session_hours": 3}', 'medium'),
('device_switching', 'Frequent device changes during study', '{"max_devices_per_day": 3, "min_session_time": 300}', 'high'),
('night_study_patterns', 'Excessive study during night hours', '{"night_hours": [0, 1, 2, 3, 4, 5], "max_night_percentage": 0.7}', 'low'),
('answering_speed', 'Unrealistic question answering speed', '{"max_questions_per_minute": 10, "min_think_time": 30}', 'high');

-- Create view for fraud dashboard
CREATE OR REPLACE VIEW fraud_dashboard AS
SELECT 
    u.user_id,
    u.real_name,
    u.nickname,
    COALESCE(fraud_stats.fraud_score, 0) as fraud_score,
    COALESCE(fraud_stats.fraud_count, 0) as fraud_count,
    COALESCE(fraud_stats.last_fraud_date, NULL) as last_fraud_date,
    COALESCE(restriction_stats.is_restricted, FALSE) as is_restricted,
    COALESCE(restriction_stats.restriction_expires, NULL) as restriction_expires
FROM users u
LEFT JOIN (
    SELECT 
        user_id,
        get_user_fraud_score(user_id, 30) as fraud_score,
        COUNT(*) as fraud_count,
        MAX(created_at) as last_fraud_date
    FROM fraud_detection_logs
    WHERE is_fraud = TRUE
    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
) fraud_stats ON u.user_id = fraud_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        TRUE as is_restricted,
        MAX(expires_at) as restriction_expires
    FROM user_restrictions
    WHERE expires_at > NOW()
    GROUP BY user_id
) restriction_stats ON u.user_id = restriction_stats.user_id;

COMMENT ON TABLE fraud_detection_logs IS 'Logs of fraud detection results';
COMMENT ON TABLE suspicious_sessions IS 'Sessions flagged as suspicious';
COMMENT ON TABLE user_restrictions IS 'Active user restrictions and limitations';
COMMENT ON TABLE device_fingerprints IS 'Device fingerprinting for security';
COMMENT ON TABLE study_session_validations IS 'Validation results for study sessions';
COMMENT ON TABLE fraud_patterns IS 'Defined fraud detection patterns';

COMMENT ON FUNCTION detect_fraud_patterns IS 'Detect common fraud patterns for a user';
COMMENT ON FUNCTION get_user_fraud_score IS 'Calculate overall fraud score for a user';
COMMENT ON FUNCTION is_user_restricted IS 'Check if user has active restrictions';
COMMENT ON FUNCTION log_fraud_detection IS 'Log a fraud detection event';
COMMENT ON FUNCTION add_user_restriction IS 'Add a restriction to a user';
COMMENT ON FUNCTION validate_study_session IS 'Validate a study session for fraud';
