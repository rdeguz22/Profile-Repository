from db import get_connection

class Set:
    @staticmethod
    def add_set(exercise_id, reps, weight, rest_time):
        conn = get_connection()
        conn.execute("""
            INSERT INTO sets (exercise_id, reps, weight, rest_time)
            VALUES (?, ?, ?, ?)
        """, (exercise_id, reps, weight, rest_time))
        conn.commit()
        conn.close()
        print("Set added.")

    @staticmethod
    def get_sets(exercise_id):
        conn = get_connection()
        c = conn.execute("""
            SELECT set_id, reps, weight, rest_time
            FROM sets
            WHERE exercise_id = ?
        """, (exercise_id,))
        sets = c.fetchall()
        conn.close()
        return sets
    
    @staticmethod
    def list_sets():
        conn = get_connection()
        c = conn.execute("SELECT * FROM sets")
        sets = c.fetchall()
        conn.close()
        return sets