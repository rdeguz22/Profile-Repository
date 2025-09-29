from db import get_connection

class Goal:
    def __init__(self, user_id, category, target_amount, deadline):
        self.user_id = user_id
        self.category = category
        self.target_amount = target_amount
        self.deadline = deadline

    def save(self):
        c = get_connection()
        c.execute("""
            INSERT INTO goals (user_id, category, target_amount, deadline)
            VALUES (?, ?, ?, ?)
        """, (self.user_id, self.category, self.target_amount, self.deadline))
        c.commit()
        c.close()
        print("Goal saved.")
    
    @staticmethod
    def add_goal(user_id, category, target_amount, deadline):
        c = get_connection()
        c.execute("""
            INSERT INTO goals (user_id, category, target_amount, deadline)
            VALUES (?, ?, ?, ?)
        """, (user_id, category, target_amount, deadline))
        c.commit()
        c.close()
        print("Goal added.")

    @staticmethod
    def get_goals(user_id):
        c = get_connection()
        c1 = c.execute("""
            SELECT goal_id, category, target_amount, deadline
            FROM goals
            WHERE user_id = ?
        """, (user_id,))
        goals = c1.fetchall()
        c.close()
        return goals