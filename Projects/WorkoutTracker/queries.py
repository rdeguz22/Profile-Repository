import sqlite3

def get_connection():
    conn = sqlite3.connect("workout_tracker.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_user(username):
    conn = get_connection()
    conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()

def get_user(username):
    conn = get_connection()
    c = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

def get_workouts(user_id):
    conn = get_connection()
    c = conn.execute("""
        SELECT workout_id, workout_date, workout_type, notes
        FROM workouts
        WHERE user_id = ?
        ORDER BY workout_date DESC
    """, (user_id,))
    return c.fetchall()

def add_workout(user_id, workout_date, workout_type, notes):
    conn = get_connection()
    conn.execute("""
        INSERT INTO workouts (user_id, workout_date, workout_type, notes)
        VALUES (?, ?, ?, ?)
    """, (user_id, workout_date, workout_type, notes))
    conn.commit()

def get_exercises(workout_id):
    conn = get_connection()
    c = conn.execute("""
        SELECT exercise_id, exercise_name, muscle_group
        FROM exercises
        WHERE workout_id = ?
    """, (workout_id,))
    return c.fetchall()

def add_exercise(workout_id, exercise_name, muscle_group):
    conn = get_connection()
    conn.execute("""
        INSERT INTO exercises (workout_id, exercise_name, muscle_group)
        VALUES (?, ?, ?)
    """, (workout_id, exercise_name, muscle_group))
    conn.commit()

def get_sets(exercise_id):
    conn = get_connection()
    c = conn.execute("""
        SELECT set_id, reps, weight, rest_time
        FROM sets
        WHERE exercise_id = ?
    """, (exercise_id,))
    return c.fetchall()

def get_progress(user_id):
    conn = get_connection()
    c = conn.execute("""
        SELECT g.exercise_name,
               g.target_weight,
               MAX(s.weight) as max_weight,
               g.target_reps,
               MAX(s.reps) as max_reps
        FROM goals g
        LEFT JOIN exercises e ON g.exercise_name = e.exercise_name
        LEFT JOIN sets s ON e.exercise_id = s.exercise_id
        WHERE g.user_id = ?
        GROUP BY g.exercise_name, g.target_weight, g.target_reps
    """, (user_id,))
    return c.fetchall()

def add_goal(user_id, exercise_name, target_weight, target_reps):
    conn = get_connection()
    conn.execute("""
        INSERT INTO goals (user_id, exercise_name, target_weight, target_reps)
        VALUES (?, ?, ?, ?)
    """, (user_id, exercise_name, target_weight, target_reps))
    conn.commit()
