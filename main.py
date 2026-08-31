from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.websocket import router as websocket_router
from app.database.database import Base, engine
from app.database import models
#create the FastAPI application
app= FastAPI()
#create the database tables
Base.metadata.create_all(bind=engine)
#register the websocket routes
app.include_router(websocket_router)
#serve static files such as CSS,JavaScript,and images
app.mount("/static",StaticFiles(directory="static"),name="static")
#serve the chatbot home page
@app.get("/")
def home():
    return FileResponse("templates/index.html")