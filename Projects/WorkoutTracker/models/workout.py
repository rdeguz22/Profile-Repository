from db import get_connection

class Workout:
    @staticmethod
    def add_workout(user_id, workout_date, workout_type, notes):
        conn = get_connection()
        conn.execute("""
            INSERT INTO workouts (user_id, workout_date, workout_type, notes)
            VALUES (?, ?, ?, ?)
        """, (user_id, workout_date, workout_type, notes))
        conn.commit()
        conn.close()
        print("Workout added.")

    @staticmethod
    def get_workouts(user_id):
        conn = get_connection()
        c = conn.execute("""
            SELECT workout_id, workout_date, workout_type, notes
            FROM workouts
            WHERE user_id = ?
            ORDER BY workout_date DESC
        """, (user_id,))
        workouts = c.fetchall()
        conn.close()
        return workouts
    
    @staticmethod
    def list_workouts():
        conn = get_connection()
        c = conn.execute("SELECT * FROM workouts")
        workouts = c.fetchall()
        conn.close()
        return workouts