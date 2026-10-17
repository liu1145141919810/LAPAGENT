import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import configparser
import os

from Crypto.cryptography import Crypto
# Using the abstract path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_configuration.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

# One dp_path file for one DataBase Class
#========== Following is the definition of different DataBase Themselves==============#
Base = declarative_base()
class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    AI_name = Column(String, nullable=False)
    # It's the created time of conversation
    timestamp = Column(DateTime, default=datetime.now)
class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    conversation_id = Column(
        Integer,
        ForeignKey('conversations.id'), 
        nullable=False)
    role_id = Column(
        Integer,
        ForeignKey('roles.id'), 
        nullable=False)
    # It's the created time of message
    timestamp = Column(DateTime, default=datetime.now)
#========== The Public DataBase Interface for all ====================================#
class DataBaseInterface:
    def __init__(self,dp_path=None):
        # load the db file here
        if dp_path is None:
            rel_path = cfg.get('database', 'db_path')
            dp_path = os.path.normpath(os.path.join(_current_dir, rel_path))
        self.db_path = dp_path
        self.crypto=Crypto()
        
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
        encrypted_data = self.crypto.encode(data.encode())
        encrypted_time = self.crypto.encode(timestamp.encode())

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (message, timestamp) VALUES (?, ?)",
                (encrypted_data, encrypted_time)
            )
            conn.commit()
