from db import get_connection

class Goal:
    @staticmethod
    def add_goal(user_id, exercise_name, target_weight, target_reps):
        conn = get_connection()
        conn.execute("""
            INSERT INTO goals (user_id, exercise_name, target_weight, target_reps)
            VALUES (?, ?, ?, ?)
        """, (user_id, exercise_name, target_weight, target_reps))
        conn.commit()
        conn.close()
        print("Goal added.")

    @staticmethod
    def get_goals(user_id):
        conn = get_connection()
        c = conn.execute("""
            SELECT goal_id, exercise_name, target_weight, target_reps
            FROM goals
            WHERE user_id = ?
        """, (user_id,))
        goals = c.fetchall()
        conn.close()
        return goals
    
    @staticmethod
    def list_goals():
        conn = get_connection()
        c = conn.execute("SELECT * FROM goals")
        goals = c.fetchall()
        conn.close()
        return goals