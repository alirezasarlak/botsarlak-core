-- Migration: 009_onboarding_states_table.sql
-- Description: Create onboarding_states table for conversation state persistence
-- Date: 2025-01-21
-- Version: v3.2.0-ai-coach-system

-- Create onboarding_states table
CREATE TABLE IF NOT EXISTS onboarding_states (
    user_id BIGINT PRIMARY KEY,
    language VARCHAR(2),
    display_name VARCHAR(100),
    nickname VARCHAR(50),
    study_track VARCHAR(50),
    grade_level VARCHAR(50),
    target_year INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_onboarding_states_user_id ON onboarding_states(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_states_created_at ON onboarding_states(created_at);

-- Add comments
COMMENT ON TABLE onboarding_states IS 'Stores user onboarding conversation states';
COMMENT ON COLUMN onboarding_states.user_id IS 'Telegram user ID';
COMMENT ON COLUMN onboarding_states.language IS 'Selected language (fa/en)';
COMMENT ON COLUMN onboarding_states.display_name IS 'User display name';
COMMENT ON COLUMN onboarding_states.nickname IS 'User nickname';
COMMENT ON COLUMN onboarding_states.study_track IS 'Selected study track';
COMMENT ON COLUMN onboarding_states.grade_level IS 'Selected grade level';
COMMENT ON COLUMN onboarding_states.target_year IS 'Target exam year';
COMMENT ON COLUMN onboarding_states.created_at IS 'State creation timestamp';
COMMENT ON COLUMN onboarding_states.updated_at IS 'State last update timestamp';
