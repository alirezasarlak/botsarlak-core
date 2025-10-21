-- Audit Logs Table for Security & Audit System
-- Comprehensive audit logging for security monitoring

-- ==================== AUDIT LOGS TABLE ====================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    security_level VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- Audit logs indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_security_level ON audit_logs(security_level);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_created ON audit_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_created ON audit_logs(action, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_security_created ON audit_logs(security_level, created_at);

-- ==================== PARTITIONING (Optional) ====================
-- For high-volume systems, consider partitioning by date
-- CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ==================== RETENTION POLICY ====================
-- Create a function to automatically clean up old audit logs
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete logs older than 90 days
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup action
    INSERT INTO audit_logs (user_id, action, resource, details, security_level)
    VALUES (
        NULL,
        'system_event',
        'audit_cleanup',
        jsonb_build_object('deleted_count', deleted_count, 'retention_days', 90),
        'info'
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ==================== SECURITY VIEWS ====================
-- View for security violations
CREATE OR REPLACE VIEW security_violations AS
SELECT 
    user_id,
    action,
    resource,
    details,
    ip_address,
    created_at
FROM audit_logs 
WHERE security_level IN ('error', 'critical') 
   OR action = 'security_violation'
ORDER BY created_at DESC;

-- View for user activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    user_id,
    COUNT(*) as total_actions,
    COUNT(DISTINCT action) as unique_actions,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MIN(created_at) as first_activity,
    MAX(created_at) as last_activity
FROM audit_logs 
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY total_actions DESC;

-- View for daily activity stats
CREATE OR REPLACE VIEW daily_activity_stats AS
SELECT 
    DATE(created_at) as activity_date,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(CASE WHEN security_level = 'critical' THEN 1 END) as critical_events,
    COUNT(CASE WHEN security_level = 'error' THEN 1 END) as error_events,
    COUNT(CASE WHEN security_level = 'warning' THEN 1 END) as warning_events
FROM audit_logs 
GROUP BY DATE(created_at)
ORDER BY activity_date DESC;

-- ==================== TRIGGERS ====================
-- Trigger to automatically log schema changes
CREATE OR REPLACE FUNCTION log_schema_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (action, resource, details, security_level)
    VALUES (
        'system_event',
        'schema_change',
        jsonb_build_object(
            'table_name', TG_TABLE_NAME,
            'operation', TG_OP,
            'old_data', CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
            'new_data', CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN to_jsonb(NEW) ELSE NULL END
        ),
        'info'
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to critical tables (optional)
-- CREATE TRIGGER trigger_users_audit
--     AFTER INSERT OR UPDATE OR DELETE ON users
--     FOR EACH ROW EXECUTE FUNCTION log_schema_changes();

-- ==================== INITIAL AUDIT LOG ====================
-- Log the creation of audit system
INSERT INTO audit_logs (action, resource, details, security_level)
VALUES (
    'system_event',
    'audit_system_init',
    jsonb_build_object(
        'version', '3.0.0',
        'description', 'Audit logging system initialized',
        'features', jsonb_build_array(
            'rate_limiting',
            'suspicious_activity_detection',
            'security_summary',
            'automatic_cleanup'
        )
    ),
    'info'
);

-- ==================== SECURITY POLICIES ====================
-- Row Level Security (RLS) policies for audit logs
-- Only allow access to audit logs for admin users

-- Enable RLS on audit_logs table
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Policy for admin access
CREATE POLICY audit_logs_admin_policy ON audit_logs
    FOR ALL
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.user_id = current_setting('app.current_user_id')::BIGINT 
            AND users.user_id = (SELECT user_id FROM users WHERE user_id = 7630624621 LIMIT 1)
        )
    );

-- ==================== MONITORING QUERIES ====================
-- Useful queries for monitoring and analysis

-- Query to find suspicious activity patterns
-- SELECT 
--     user_id,
--     COUNT(*) as action_count,
--     array_agg(DISTINCT action) as actions,
--     MIN(created_at) as first_action,
--     MAX(created_at) as last_action
-- FROM audit_logs 
-- WHERE created_at > NOW() - INTERVAL '1 hour'
-- GROUP BY user_id
-- HAVING COUNT(*) > 50
-- ORDER BY action_count DESC;

-- Query to find failed login attempts
-- SELECT 
--     user_id,
--     ip_address,
--     COUNT(*) as failed_attempts,
--     MAX(created_at) as last_attempt
-- FROM audit_logs 
-- WHERE action = 'user_login' 
--   AND security_level = 'error'
--   AND created_at > NOW() - INTERVAL '24 hours'
-- GROUP BY user_id, ip_address
-- HAVING COUNT(*) > 5
-- ORDER BY failed_attempts DESC;



