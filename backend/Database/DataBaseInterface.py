from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime
import configparser
import os

from Crypto.cryptography import Crypto
from .DataDefine import (
    Base,
    Roles,
    AI_Models,
    Conversation,
    Messages,
    provider_list,
    validate_model_name,
    validate_role_name,
)
from public.logger import setup_logger
logger = setup_logger(__name__)
from public.util import PublicToolKit

# Using the abstract path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

#========== The Public DataBase Interface for all ====================================#
class DataBaseInterface:
    def __init__(self,dp_path=None):

        database_url = os.getenv('LAPAGENT_DATABASE_URL') or cfg.get('database', 'database_url', fallback=None)
        if dp_path and '://' in str(dp_path):
            database_url = str(dp_path)
        if database_url:
            engine = create_engine(database_url, echo=False,pool_pre_ping=True)
            self.db_path = database_url

            cfg.set('database', 'database_url', database_url)
            with open(_config_path, 'w') as configfile:
                cfg.write(configfile)
        else:
            if dp_path is None:
                env_db_path = os.getenv('LAPAGENT_DB_PATH')
                rel_path = env_db_path or cfg.get('database', 'db_path')
                if os.path.isabs(rel_path):
                    dp_path = rel_path
                else:
                    dp_path = os.path.normpath(os.path.join(_current_dir, rel_path))
            self.db_path = dp_path
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            #echo: whether to log SQL statements; False means no logging
            engine = create_engine(f"sqlite:///{self.db_path}", echo=False)

        self.crypto = Crypto()
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine)
        with self.SessionLocal() as session:
            for role_name in ("user", "system", "agent"):
                validate_role_name(role_name)
            if session.query(Roles).count() == 0:
                session.add_all([Roles(name='user'), Roles(name='system'), Roles(name='agent')],)
            existing_models = session.query(AI_Models).all()
            for m in provider_list:
                validate_model_name(m)
                if m not in [model.name for model in existing_models]:
                    session.add(AI_Models(name=m))
            session.commit()
    def all_history(self):
        all_history = []
        with self.SessionLocal() as s:
            for c in s.query(Conversation).all():
                #delete the converstaion half year ago
                timestamp = c.timestamp
                if (datetime.now() - timestamp).days > 180:
                    s.delete(c)
                    s.commit()
                    continue
                conversation_history = {
                    "conversation_id": c.id,
                    "AI_Model": s.query(AI_Models).filter(AI_Models.id == c.AI_Model_id).first().name,
                    "timestamp": timestamp,
                }
                all_history.append(conversation_history)
        return all_history
    def store_message(self,data):
        timestamp = datetime.now()
        message = data.get("message")

        msg = Messages(
            message=self.crypto.encode(message.encode()),
            conversation_id=data.get("conversation_id"),
            role_id=data.get("role_id"),
            timestamp=timestamp
        )
        with self.SessionLocal() as s:
            s.add(msg)
            s.commit()
    def new_conversation(self,model_name):
        with self.SessionLocal() as s:
            model = s.query(AI_Models).filter(AI_Models.name == model_name).first()
            if not model:
                raise ValueError(f"Model '{model_name}' not found in the database.")
            new_conversation = Conversation(AI_Model_id=model.id,)
            s.add(new_conversation)
            s.commit()

            logger.info(f"the index is {new_conversation.id}")
            return new_conversation.id
        
    def del_conversation(self,conversation_id):
        with self.SessionLocal() as s:
            conversation = s.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                raise ValueError(f"Conversation with ID '{conversation_id}' not found.")
            s.delete(conversation)
            s.commit()
    def load_conversation(self,conversation_id):
        all_messages = []
        with self.SessionLocal() as s:
            for c in s.query(Messages).filter(Messages.conversation_id == conversation_id).order_by(Messages.timestamp).all():
                message_data = {
                    "message": self.crypto.decode(c.message),
                    "role_id": c.role_id,
                    "timestamp": c.timestamp,
                }
                all_messages.append(message_data)
        return all_messages
    def check_role(self,role_name):
        with self.SessionLocal() as s:
            role = s.query(Roles).filter(Roles.name == role_name).first()
            if not role:
                logger.error("Error: Role not found")
                return None
            return role.id
    def check_role_name(self,role_id):
        with self.SessionLocal() as s:
            role = s.query(Roles).filter(Roles.id == role_id).first()
            if not role:
                logger.error("Error: Role not found")
                return None
            return role.name