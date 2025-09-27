import sqlite3

DB_PATH = 'workout_tracker.db'

def get_connection():
    return sqlite3.connect(DB_PATH)