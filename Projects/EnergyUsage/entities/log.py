from db import get_connection

class Log:
    def __init__(self, user_id, log_date, category, amount, unit):
        self.user_id = user_id
        self.log_date = log_date
        self.category = category
        self.amount = amount
        self.unit = unit

    def save(self):
        c = get_connection()
        c.execute("""
            INSERT INTO energy_logs (user_id, log_date, category, amount, unit)
            VALUES (?, ?, ?, ?, ?)
        """, (self.user_id, self.log_date, self.category, self.amount, self.unit))
        c.commit()
        c.close()
        print("Log saved.")

    @staticmethod
    def add_log(user_id, log_date, category, amount, unit):
        c = get_connection()
        c.execute("""
            INSERT INTO energy_logs (user_id, log_date, category, amount, unit)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, log_date, category, amount, unit))
        c.commit()
        c.close()
        print("Log added.")

    @staticmethod
    def get_logs(user_id):
        c = get_connection()
        c1 = c.execute("""
            SELECT log_id, log_date, category, amount, unit
            FROM energy_logs
            WHERE user_id = ?
            ORDER BY log_date DESC
        """, (user_id,))
        logs = c1.fetchall()
        c.close()
        return logs