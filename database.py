import sqlite3
from datetime import datetime
from hashlib import sha256

DB_NAME = 'user_data.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, full_name TEXT, email TEXT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY, username TEXT, activity TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

def create_user(full_name, email, username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO users (full_name, email, username, password) VALUES (?, ?, ?, ?)', 
              (full_name, email, username, hash_password(password)))
    conn.commit()
    conn.close()

def log_user_activity(username, activity):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO logs (username, activity, timestamp) VALUES (?, ?, ?)', 
              (username, activity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def get_user_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT username, timestamp, activity FROM logs')
    rows = c.fetchall()
    conn.close()
    return rows

def update_user_credentials(old_username, email, new_username, new_password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=? AND email=?', (old_username, email))
    row = c.fetchone()
    if row:
        user_id = row[0]
        c.execute('UPDATE users SET username=?, password=? WHERE id=?', 
                  (new_username, hash_password(new_password), user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()