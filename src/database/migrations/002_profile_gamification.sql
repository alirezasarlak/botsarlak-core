-- 🌌 SarlakBot v2.4.0 - Profile & Gamification Migration
-- Additive migration - safe to run multiple times

-- Add profile fields to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS province VARCHAR(100),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS school_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS exam_brand VARCHAR(50),
ADD COLUMN IF NOT EXISTS exam_tscore_avg DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS took_konkur BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS konkur_times INTEGER,
ADD COLUMN IF NOT EXISTS last_konkur_rank VARCHAR(20),
ADD COLUMN IF NOT EXISTS has_advisor BOOLEAN,
ADD COLUMN IF NOT EXISTS target_major VARCHAR(100),
ADD COLUMN IF NOT EXISTS target_university VARCHAR(100),
ADD COLUMN IF NOT EXISTS target_city VARCHAR(100),
ADD COLUMN IF NOT EXISTS profile_public BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS public_profile_id VARCHAR(20) UNIQUE;

-- Create user_gamification table
CREATE TABLE IF NOT EXISTS user_gamification (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    badge VARCHAR(50) DEFAULT 'Novice 🚀',
    last_calculated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create study_reports table for gamification calculation
CREATE TABLE IF NOT EXISTS study_reports (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    study_minutes INTEGER NOT NULL DEFAULT 0,
    tests_count INTEGER NOT NULL DEFAULT 0,
    report_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, report_date)
);

-- Add report_date column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'study_reports' AND column_name = 'report_date') THEN
        ALTER TABLE study_reports ADD COLUMN report_date DATE DEFAULT CURRENT_DATE;
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_public_profile_id ON users(public_profile_id);
CREATE INDEX IF NOT EXISTS idx_user_gamification_points ON user_gamification(points DESC);
CREATE INDEX IF NOT EXISTS idx_study_reports_user_date ON study_reports(user_id, report_date);
CREATE INDEX IF NOT EXISTS idx_study_reports_date ON study_reports(report_date);

-- Create function to generate public profile ID
CREATE OR REPLACE FUNCTION generate_public_profile_id(tg_id BIGINT) 
RETURNS VARCHAR(20) AS $$
DECLARE
    base36_str VARCHAR(20);
    checksum_str VARCHAR(2);
    result VARCHAR(20);
BEGIN
    -- Convert to base36
    base36_str := '';
    WHILE tg_id > 0 LOOP
        base36_str := CHR(CASE (tg_id % 36)
            WHEN 0 THEN 48  -- '0'
            WHEN 1 THEN 49  -- '1'
            WHEN 2 THEN 50  -- '2'
            WHEN 3 THEN 51  -- '3'
            WHEN 4 THEN 52  -- '4'
            WHEN 5 THEN 53  -- '5'
            WHEN 6 THEN 54  -- '6'
            WHEN 7 THEN 55  -- '7'
            WHEN 8 THEN 56  -- '8'
            WHEN 9 THEN 57  -- '9'
            WHEN 10 THEN 65 -- 'A'
            WHEN 11 THEN 66 -- 'B'
            WHEN 12 THEN 67 -- 'C'
            WHEN 13 THEN 68 -- 'D'
            WHEN 14 THEN 69 -- 'E'
            WHEN 15 THEN 70 -- 'F'
            WHEN 16 THEN 71 -- 'G'
            WHEN 17 THEN 72 -- 'H'
            WHEN 18 THEN 73 -- 'I'
            WHEN 19 THEN 74 -- 'J'
            WHEN 20 THEN 75 -- 'K'
            WHEN 21 THEN 76 -- 'L'
            WHEN 22 THEN 77 -- 'M'
            WHEN 23 THEN 78 -- 'N'
            WHEN 24 THEN 79 -- 'O'
            WHEN 25 THEN 80 -- 'P'
            WHEN 26 THEN 81 -- 'Q'
            WHEN 27 THEN 82 -- 'R'
            WHEN 28 THEN 83 -- 'S'
            WHEN 29 THEN 84 -- 'T'
            WHEN 30 THEN 85 -- 'U'
            WHEN 31 THEN 86 -- 'V'
            WHEN 32 THEN 87 -- 'W'
            WHEN 33 THEN 88 -- 'X'
            WHEN 34 THEN 89 -- 'Y'
            WHEN 35 THEN 90 -- 'Z'
        END) || base36_str;
        tg_id := tg_id / 36;
    END LOOP;
    
    -- Generate checksum
    checksum_str := LPAD(((tg_id * 97) % 1296)::TEXT, 2, '0');
    
    result := 'SB-' || base36_str || '-' || checksum_str;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-generate public profile ID
CREATE OR REPLACE FUNCTION trigger_generate_public_id() 
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.public_profile_id IS NULL THEN
        NEW.public_profile_id := generate_public_profile_id(NEW.user_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (PostgreSQL doesn't support IF NOT EXISTS for triggers)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_users_public_id') THEN
        CREATE TRIGGER trigger_users_public_id
            BEFORE INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION trigger_generate_public_id();
    END IF;
END $$;

-- Update existing users with public profile IDs
UPDATE users 
SET public_profile_id = generate_public_profile_id(user_id)
WHERE public_profile_id IS NULL;

-- Create gamification calculation function
CREATE OR REPLACE FUNCTION recalc_user_gamification(target_user_id BIGINT)
RETURNS TABLE(points INTEGER, level INTEGER, badge VARCHAR(50)) AS $$
DECLARE
    total_points INTEGER := 0;
    calculated_level INTEGER := 1;
    calculated_badge VARCHAR(50) := 'Novice 🚀';
    daily_bonus_points INTEGER := 0;
    study_minutes_today INTEGER;
    tests_today INTEGER;
BEGIN
    -- Calculate points from study reports
    SELECT 
        COALESCE(SUM(study_minutes / 5), 0) + COALESCE(SUM(tests_count * 2), 0)
    INTO total_points
    FROM study_reports 
    WHERE user_id = target_user_id;
    
    -- Get today's stats for daily bonus
    SELECT 
        COALESCE(study_minutes, 0),
        COALESCE(tests_count, 0)
    INTO study_minutes_today, tests_today
    FROM study_reports 
    WHERE user_id = target_user_id AND report_date = CURRENT_DATE;
    
    -- Daily bonuses
    IF study_minutes_today >= 240 THEN
        daily_bonus_points := daily_bonus_points + 10;
    END IF;
    
    IF tests_today >= 50 THEN
        daily_bonus_points := daily_bonus_points + 5;
    END IF;
    
    total_points := total_points + daily_bonus_points;
    
    -- Calculate level (floor(points/1000) + 1)
    calculated_level := FLOOR(total_points / 1000) + 1;
    
    -- Determine badge
    IF calculated_level >= 10 THEN
        calculated_badge := 'Master 🌟';
    ELSIF calculated_level >= 5 THEN
        calculated_badge := 'Challenger ⚔️';
    ELSIF calculated_level >= 2 THEN
        calculated_badge := 'Focused 🧠';
    ELSE
        calculated_badge := 'Novice 🚀';
    END IF;
    
    -- Update or insert gamification record
    INSERT INTO user_gamification (user_id, points, level, badge, last_calculated_at, updated_at)
    VALUES (target_user_id, total_points, calculated_level, calculated_badge, NOW(), NOW())
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        points = total_points,
        level = calculated_level,
        badge = calculated_badge,
        last_calculated_at = NOW(),
        updated_at = NOW();
    
    RETURN QUERY SELECT total_points, calculated_level, calculated_badge;
END;
$$ LANGUAGE plpgsql;

-- Create profile completion calculation function
CREATE OR REPLACE FUNCTION calculate_profile_completion(target_user_id BIGINT)
RETURNS INTEGER AS $$
DECLARE
    completion_score INTEGER := 0;
    user_record RECORD;
BEGIN
    SELECT * INTO user_record FROM users WHERE user_id = target_user_id;
    
    -- real_name (10 points)
    IF user_record.real_name IS NOT NULL AND user_record.real_name != '' THEN
        completion_score := completion_score + 10;
    END IF;
    
    -- nickname (10 points)
    IF user_record.nickname IS NOT NULL AND user_record.nickname != '' THEN
        completion_score := completion_score + 10;
    END IF;
    
    -- track + band/year (15 points)
    IF user_record.study_track IS NOT NULL AND user_record.grade_band IS NOT NULL AND user_record.grade_year IS NOT NULL THEN
        completion_score := completion_score + 15;
    END IF;
    
    -- phone (5 points)
    IF user_record.phone IS NOT NULL AND user_record.phone != '' THEN
        completion_score := completion_score + 5;
    END IF;
    
    -- province+city (10 points)
    IF user_record.province IS NOT NULL AND user_record.city IS NOT NULL THEN
        completion_score := completion_score + 10;
    END IF;
    
    -- school_type (5 points)
    IF user_record.school_type IS NOT NULL AND user_record.school_type != '' THEN
        completion_score := completion_score + 5;
    END IF;
    
    -- exam_brand (+ tscore if set) (10 points)
    IF user_record.exam_brand IS NOT NULL AND user_record.exam_brand != '' THEN
        IF user_record.exam_tscore_avg IS NOT NULL THEN
            completion_score := completion_score + 10;
        ELSE
            completion_score := completion_score + 5;
        END IF;
    END IF;
    
    -- took_konkur (+ times + last_rank if set) (10 points)
    IF user_record.took_konkur IS NOT NULL THEN
        IF user_record.took_konkur = TRUE AND user_record.konkur_times IS NOT NULL AND user_record.last_konkur_rank IS NOT NULL THEN
            completion_score := completion_score + 10;
        ELSIF user_record.took_konkur = TRUE THEN
            completion_score := completion_score + 5;
        ELSE
            completion_score := completion_score + 5;
        END IF;
    END IF;
    
    -- has_advisor (5 points)
    IF user_record.has_advisor IS NOT NULL THEN
        completion_score := completion_score + 5;
    END IF;
    
    -- target_major (10 points)
    IF user_record.target_major IS NOT NULL AND user_record.target_major != '' THEN
        completion_score := completion_score + 10;
    END IF;
    
    -- target_university + target_city (10 points)
    IF user_record.target_university IS NOT NULL AND user_record.target_city IS NOT NULL THEN
        completion_score := completion_score + 10;
    ELSIF user_record.target_university IS NOT NULL OR user_record.target_city IS NOT NULL THEN
        completion_score := completion_score + 5;
    END IF;
    
    RETURN completion_score;
END;
$$ LANGUAGE plpgsql;
