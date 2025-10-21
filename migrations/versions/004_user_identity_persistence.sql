-- Enhanced user identity persistence system
-- Ensures user data is never lost across bot restarts

-- Add missing columns to users table if they don't exist
DO $$ 
BEGIN
    -- Add is_active column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'is_active') THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add last_seen_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_seen_at') THEN
        ALTER TABLE users ADD COLUMN last_seen_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
    
    -- Add streak column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'streak') THEN
        ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0;
    END IF;
    
    -- Add total_minutes column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'total_minutes') THEN
        ALTER TABLE users ADD COLUMN total_minutes INTEGER DEFAULT 0;
    END IF;
    
    -- Add daily_goal column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'daily_goal') THEN
        ALTER TABLE users ADD COLUMN daily_goal INTEGER DEFAULT 240;
    END IF;
    
    -- Add data_version column for tracking data changes
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'data_version') THEN
        ALTER TABLE users ADD COLUMN data_version INTEGER DEFAULT 1;
    END IF;
END $$;

-- Create unique index on user_id if it doesn't exist
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);

-- Create index for active users
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = TRUE;

-- Create index for last seen tracking
CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen_at);

-- Update existing users to have proper defaults
UPDATE users 
SET 
    is_active = COALESCE(is_active, TRUE),
    last_seen_at = COALESCE(last_seen_at, created_at),
    streak = COALESCE(streak, 0),
    total_minutes = COALESCE(total_minutes, 0),
    daily_goal = COALESCE(daily_goal, 240),
    data_version = COALESCE(data_version, 1)
WHERE is_active IS NULL 
   OR last_seen_at IS NULL 
   OR streak IS NULL 
   OR total_minutes IS NULL 
   OR daily_goal IS NULL 
   OR data_version IS NULL;



