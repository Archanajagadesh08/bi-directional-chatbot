from sqlalchemy import Column, Integer, String, Text,DateTime,ForeignKey,Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum
from datetime import datetime
from app.database.database import Base
#enums
class ConversationMode(PyEnum):
    coding ="coding"
    writing ="writing"
    study ="study"
    research ="research"
    general ="general"
class MessageRole(PyEnum):
    user ="user"
    assistant ="assistant"
#user model
class User(Base):
    __tablename__="users"
    user_id = Column(UUID(as_uuid = True),primary_key=True,default=uuid.uuid4)
    username = Column(String(100),unique=True, nullable=False)
    email = Column(String(225), unique=True,nullable=False)
    password_hash = Column(String(225),nullable=False)
    created_at = Column(DateTime,default= datetime.utcnow)
    updated_at = Column(DateTime, default= datetime.utcnow)
#conversation model
class Conversation(Base):
    __tablename__ = "conversations"
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    title = Column(String, nullable=False)
    mode = Column(Enum(ConversationMode), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
#message model
class Message(Base):
    __tablename__ = "messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
#attachment model
class Attachment(Base):
    __tablename__ = "attachments"
    attachment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.message_id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

