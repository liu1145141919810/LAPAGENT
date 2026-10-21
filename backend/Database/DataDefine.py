from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Enum,Integer,ForeignKey,DateTime,String
from sqlalchemy.orm import relationship

from datetime import datetime

from public.AI_configure import base_url_dict
provider_list = list(base_url_dict.keys())

Base = declarative_base()

class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum('user', 'system','agent'), nullable=False)
class AI_Models(Base):
    __tablename__ = "AI_Models"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(*provider_list), nullable=False)
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    AI_Model_id = Column(Integer,ForeignKey('AI_Models.id'), nullable=False)
    # It's the created time of conversation
    timestamp = Column(DateTime, default=datetime.now)

    messages = relationship(
        "Messages",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

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

    conversation = relationship("Conversation", back_populates="messages")