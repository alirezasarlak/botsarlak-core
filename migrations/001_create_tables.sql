CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    nickname TEXT,
    phone TEXT,
    major TEXT,
    points INT DEFAULT 0,
    joined_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    day_jalali TEXT,
    start_dt TIMESTAMPTZ,
    end_dt TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS study_entries (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES study_sessions(id) ON DELETE CASCADE,
    subject TEXT,
    topic TEXT,
    tests INT,
    notes TEXT,
    dur INT
);

CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT,
    question TEXT,
    answer TEXT,
    correct_count INT DEFAULT 0,
    needs_review BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS review_calendar (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    type TEXT,
    target TEXT,
    review_date DATE,
    done BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS points_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    points INT,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS league_snapshots (
    id SERIAL PRIMARY KEY,
    period TEXT,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS missions_done (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    code TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, code)
);

CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    new_user_id BIGINT UNIQUE
);
