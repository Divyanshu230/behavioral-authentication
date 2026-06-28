 
PRAGMA foreign_keys = ON;
 
-- ----------------------------------------------------------------------------
-- Table: users
-- Stores core account/identity information for each registered user.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
 
-- ----------------------------------------------------------------------------
-- Table: behavior_profiles
-- Stores the baseline behavioral biometric profile for each user, derived
-- from keystroke dynamics (hold/flight time, typing speed) and mouse
-- dynamics (movement speed, click frequency). Used as the reference
-- "fingerprint" against which live login behavior is compared.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS behavior_profiles (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id              INTEGER NOT NULL,
    avg_hold_time        REAL,
    avg_flight_time      REAL,
    avg_typing_speed     REAL,
    avg_mouse_speed      REAL,
    avg_click_frequency  REAL,
    created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    CONSTRAINT fk_behavior_profiles_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
 
-- Speed up lookups of a user's behavior profile(s).
CREATE INDEX IF NOT EXISTS idx_behavior_profiles_user_id
    ON behavior_profiles (user_id);

CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    behavior_score REAL,

    risk_level TEXT,

    status TEXT,

    ip_address TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

SELECT COUNT(*) FROM login_history
WHERE user_id = ?;

SELECT ROUND(AVG(behavior_score),2)
FROM login_history
WHERE user_id = ?;

SELECT MAX(behavior_score)
FROM login_history
WHERE user_id = ?;

SELECT MIN(behavior_score)
FROM login_history
WHERE user_id = ?;

SELECT risk_level, COUNT(*)
FROM login_history
WHERE user_id = ?
GROUP BY risk_level;