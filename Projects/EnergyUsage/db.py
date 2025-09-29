import sqlite3

DB_PATH = "energy_usage.db"

def get_connection():
    return sqlite3.connect(DB_PATH)