-- DROP TABLE IF EXISTS users, workouts, exercises, sets, goals;

-- 1. Users Table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Workouts Table
CREATE TABLE workouts (
    workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    workout_date DATE NOT NULL,
    workout_type VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL, -- duration in minutes
    calories_burned INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Exercises Table
CREATE TABLE exercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    muscle_group VARCHAR(50),
    FOREIGN KEY (workout_id) REFERENCES workouts(workout_id) ON DELETE CASCADE
);

-- 4. Sets Table
CREATE TABLE sets (
    set_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    repetitions INTEGER NOT NULL,
    weight DECIMAL(5,2), -- weight in lbs
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id) ON DELETE CASCADE
);

-- 5. Goals Table
CREATE TABLE goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    target_weight DECIMAL(5,2),
    target_repetitions INT,
    deadline DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
