from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Conversation,Message
from app.routes.auth import get_current_user
router = APIRouter(prefix="/history", tags=["Conversation History"])
@router.get("/conversations")
def get_conversations(
    current_user = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
       Conversation.user_id == current_user.user_id 
    ).order_by(Conversation.created_at.desc()).all()
    return[
        {
            "conversation_id": str(conversation.conversation_id),
            "title": conversation.title,
            "mode": conversation.mode,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at
        }
        for conversation in conversation
    ]
@router.get("/conversations/{conversation_id}")
def get_conversation_messages(
    conversation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id,
        Conversation.user_id == current_user.user_id
    ).first()
    if not conversation:
        raise HTTPException(
            status_code = 404,
            detail="Conversation not found"   )
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.conversation_id
    ).order_by(Message.created_at.asc()).all()
    return{
        "conversation_id": str(conversation.conversation_id),
        "title": conversation.title,
        "mode": conversation.mode,
        "messages": [{
            "message_id": str(message.message_id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages]
    }