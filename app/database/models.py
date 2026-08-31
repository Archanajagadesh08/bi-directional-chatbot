from sqlalchemy import Column, Integer, String, Text,DateTime
from datetime import datetime
from app.database.database import Base
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    mode = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
