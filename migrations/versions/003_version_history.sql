-- Version history table for tracking deployments
-- This table ensures we can track all version changes and deployments

CREATE TABLE IF NOT EXISTS version_history (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    deployed_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_by VARCHAR(100),
    migration_count INTEGER DEFAULT 0,
    deployment_notes TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_version_history_version ON version_history(version);
CREATE INDEX IF NOT EXISTS idx_version_history_deployed_at ON version_history(deployed_at);

-- Insert current version
INSERT INTO version_history (version, description, deployed_by, migration_count, deployment_notes)
VALUES (
    '3.0.0',
    'Professional code quality implementation, Alembic migration system, security enhancements',
    'system',
    3,
    'Initial professional setup with all safety measures'
) ON CONFLICT DO NOTHING;



