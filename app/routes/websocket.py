import json
import asyncio
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from app.files.file_service import create_file_part
from app.schemas.gemini_schema import GeminiRequest
from app.services.gemini_service import send_to_gemini
from app.database.database import SessionLocal
from app.database.models import Message,User,Conversation,ConversationMode,MessageRole
from app.services.auth_service import validate_access_token
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID
router = APIRouter()
#WebSocket connection and authentication
@router.websocket("/ws")
async def websocket_endpoint(websocket :WebSocket,token : str):
    await websocket.accept()
    db=SessionLocal()
    current_user = validate_access_token(token,db)
    if not current_user:
        await websocket.send_text("Invalid or expired token")
        await websocket.close()
        return
    while True:
        try:
            #Receive and process client request
            data = await websocket.receive_text()
            data= json.loads(data)
            request = GeminiRequest(**data)
            #prepare message and file contents
            contents =[]
            if request.message:
                contents.append(request.message)
            if request.file:
                file_part = create_file_part(request.file)
                contents.append(file_part)
            if not contents:
                await websocket.send_text(
                    "Please enter a message or attach a file."
                )
                continue
            #send request to Gemini and return response
            response = await asyncio.to_thread(
                send_to_gemini, contents
            )
            try:
                #get existing conversation or create a new one
                if request.conversation_id:
                    conversation = db.query(Conversation).filter(
                        Conversation.conversation_id ==UUID(request.conversation_id),
                        Conversation.user_id == current_user.user_id).first()
                    if not conversation:
                        await  websocket.send_text("Conversation not found")
                        continue
                else:
                    conversation = Conversation(
                        user_id = current_user.user_id,
                        title = (request.message or "New conversation")[:100],
                        mode = ConversationMode(request.mode or "general")
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                    conversation_id = str(conversation.conversation_id)
                    #save user and assistant messages
                user_message = Message(
                    conversation_id = conversation.conversation_id,
                    role = MessageRole.user,
                    content= request.message or ""
                )
                assistant_message = Message(
                    conversation_id = conversation.conversation_id,
                    role = MessageRole.assistant,
                    content = response or ""
                )
                db.add(user_message)
                db.add(assistant_message)
                db.commit()
    
            finally:
                db.close()
                #send response to client 
            await websocket.send_text(json.dumps({
                "response": response,
                "conversation_id":conversation_id
            }))
            #Handle webSocket errors
        except WebSocketDisconnect:
            print("WebSocket disconnected")
            break
        except Exception as e:
            print(f"websocket error:{e}")
            await websocket.send_text(f"ERROR: {str(e)}")
