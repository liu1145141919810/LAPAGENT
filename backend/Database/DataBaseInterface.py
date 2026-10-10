import sqlite3
from datetime import datetime
import configparser
import os

# Using the abstract path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_configuration.ini')

cfg = configparser.ConfigParser()
cfg.read(_config_path)

# One dp_path file for one DataBase Class
class DataBaseInterface:
    def __init__(self,dp_path=None):
        if dp_path is None:
            rel_path = cfg.get('database', 'path')
            dp_path = os.path.normpath(os.path.join(_current_dir, rel_path))
        self.db_path = dp_path

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
    def store(self,data):
        #print(f"Storing data: {data}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (message, timestamp) VALUES (?, ?)",
                (data, timestamp)
            )
            conn.commit()