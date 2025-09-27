from db import get_connection

class User:
    @staticmethod
    def add_user(username, email):
        conn = get_connection()
        conn.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        conn.commit()
        conn.close()
        print(f"User {username} added.")

    @staticmethod
    def get_user(user_id):
        conn = get_connection()
        c = conn.execute("SELECT user_id, username, email FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    
    @staticmethod
    def list_users():
        conn = get_connection()
        c = conn.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()
        return users