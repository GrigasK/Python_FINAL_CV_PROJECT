import sqlite3
from app import app



def get_user(username, password):
    conn = sqlite3.connect("app/admin.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Users WHERE username=? AND password=?", (username, password))
    user_login_data = cursor.fetchone()
    conn.close()
    return user_login_data




