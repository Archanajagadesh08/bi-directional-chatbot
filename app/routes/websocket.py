import json
import asyncio
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from app.files.file_service import create_file_part
from app.schemas.gemini_schema import GeminiRequest
from app.services.gemini_service import send_to_gemini
from app.database.database import SessionLocal
from app.database.models import ChatMessage
router = APIRouter()
#WebSocket connection
@router.websocket("/ws")
async def websocket_endpoint(websocket :WebSocket):
    await websocket.accept()
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
            db = SessionLocal()
            try:
                chat_message = ChatMessage(
                    message=request.message or "",
                    response=response or "",
                    mode=request.mode or "default",)
                db.add(chat_message)
                db.commit()
            finally:
                db.close()
            await websocket.send_text(response)
            #Handle webSocket errors
        except WebSocketDisconnect:
            print("WebSocket disconnected")
            break
        except Exception as e:
            print(f"websocket error:{e}")
            await websocket.send_text(f"ERROR: {str(e)}")
