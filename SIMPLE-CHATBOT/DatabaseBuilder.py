import os
import sqlite3
from datetime import datetime
import streamlit as st
class DatabaseHandler:
    def __init__(self, db_name="chat_history.db"):
        self.db_name = db_name
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS chat_records
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              session_name TEXT,
                              role TEXT,
                              content TEXT,
                              timestamp TEXT)''')
                conn.commit()
        except sqlite3.Error as e:
            st.error(f"Database Init Error: {e}")

    def save_chat_message(self, session_name, role, content):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO chat_records (session_name, role, content, timestamp) VALUES (?, ?, ?, ?)",
                          (session_name, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
        except sqlite3.Error as e:
            st.error(f"Database Save Error: {e}")

    def load_session_messages(self, session_name):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT role, content FROM chat_records WHERE session_name = ? ORDER BY id ASC", (session_name,))
                rows = c.fetchall()
                return [{"role": r, "content": c} for r, c in rows]
        except sqlite3.Error as e:
            st.error(f" Database Load Error: {e}")
            return []

    def get_all_sessions(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT DISTINCT session_name FROM chat_records")
                rows = c.fetchall()
                return [row[0] for row in rows]
        except sqlite3.Error as e:
            st.error(f"Database Fetch Error: {e}")
            return []

    def delete_session(self, session_name):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM chat_records WHERE session_name = ?", (session_name,))
                conn.commit()
        except sqlite3.Error as e:
            st.error(f"Database Delete Error: {e}")