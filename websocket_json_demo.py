from fastapi import FastAPI,WebSocket
import uvicorn
app= FastAPI()
@app.websocket("/ws")
async def websocket_demo(websocket:WebSocket):
    await websocket.accept()
    await websocket.send_json({"role":"assistant","message":"Hello! this is a JSON websocket message."})
if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8001)
