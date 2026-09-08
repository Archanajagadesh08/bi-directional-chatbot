import json
import asyncio
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from app.files.file_service import create_file_part,save_file
from app.schemas.gemini_schema import GeminiRequest
from app.services.gemini_service import send_to_gemini
from app.database.database import SessionLocal
from app.database.models import Message,User,Conversation,ConversationMode,MessageRole,Attachment
from app.services.auth_service import validate_access_token
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.logging_config import logger
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
    current_user_id = current_user.user_id
    logger.info("User authenticated successfully")
    while True:
        try:
            #Receive and process client request
            data = await websocket.receive_text()
            data= json.loads(data)
            request = GeminiRequest(**data)
            logger.info("Request received from client")
            #prepare message and file contents
            contents =[]
            if request.message:
                contents.append(request.message)
            if request.file:
                Attachment_data = save_file(request.file)
                logger.info(f"File received:{request.file.name}")
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
            logger.info("Response received from Gemini")
            try:
                #get existing conversation or create a new one
                if request.conversation_id:
                    conversation = db.query(Conversation).filter(
                        Conversation.conversation_id ==UUID(request.conversation_id),
                        Conversation.user_id == current_user_id).first()
                    if not conversation:
                        await  websocket.send_text("Conversation not found")
                        continue
                else:
                    conversation = Conversation(
                        user_id = current_user_id,
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
                db.add(user_message)
                db.flush()
                if request.file:
                    attachment = Attachment(
                        message_id = user_message.message_id,
                        file_name = Attachment_data["file_name"],
                        file_path = Attachment_data["file_path"],
                        file_type = Attachment_data["file_type"],
                        file_size = Attachment_data["file_size"]
                    )
                    db.add(attachment)
                assistant_message = Message(
                    conversation_id = conversation.conversation_id,
                    role = MessageRole.assistant,
                    content = response or ""
                )
                db.add(assistant_message)
                db.commit()
                logger.info("Converation save:")
    
            finally:
                db.close()
                #send response to client 
            await websocket.send_text(json.dumps({
                "response": response,
                "conversation_id":conversation_id
            }))
            #Handle webSocket errors
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            break
        except Exception as e:
            print("WebSocket disconnected")
            await websocket.send_text(f"ERROR: {str(e)}")
