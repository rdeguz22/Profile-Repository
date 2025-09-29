from db import get_connection

class User:

    def __init__ (self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

    def save(self):
        c = get_connection()
        c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (self.username, self.email))
        c.commit()
        c.close()
        print(f"User {self.username} added.")

    @staticmethod
    def add_user(username, email):
        c = get_connection()
        c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        c.commit()
        c.close()
        print(f"User {username} added.")

    @staticmethod
    def get_user(user_id):
        c = get_connection()
        c1 = c.execute("SELECT user_id, username, email FROM users WHERE user_id = ?", (user_id,))
        user = c1.fetchone()
        c.close()
        return user
    
    @staticmethod
    def list_users():
        c = get_connection()
        c1 = c.execute("SELECT * FROM users")
        users = c1.fetchall()
        c.close()
        return users