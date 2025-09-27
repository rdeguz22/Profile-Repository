from db import get_connection

class Exercise:
    @staticmethod
    def add_exercise(workout_id, exercise_name, muscle_group):
        conn = get_connection()
        conn.execute("""
            INSERT INTO exercises (workout_id, exercise_name, muscle_group)
            VALUES (?, ?, ?)
        """, (workout_id, exercise_name, muscle_group))
        conn.commit()
        conn.close()
        print("Exercise added.")

    @staticmethod
    def get_exercises(workout_id):
        conn = get_connection()
        c = conn.execute("""
            SELECT exercise_id, exercise_name, muscle_group
            FROM exercises
            WHERE workout_id = ?
        """, (workout_id,))
        exercises = c.fetchall()
        conn.close()
        return exercises
    
    @staticmethod
    def list_exercises():
        conn = get_connection()
        c = conn.execute("SELECT * FROM exercises")
        exercises = c.fetchall()
        conn.close()
        return exercises
