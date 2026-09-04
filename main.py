from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.websocket import router as websocket_router
from app.routes.auth import router as auth_router
from app.database.database import Base, engine
from app.database import models
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.routes.history import router as history_router
#create the FastAPI application
app= FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:3000"],
                   allow_credentials= True,
                   allow_methods=["*"],
                   allow_headers=["*"],)
app.add_middleware(AuthMiddleware)
#create the database tables
Base.metadata.create_all(bind=engine)
#register the websocket routes
app.include_router(websocket_router)
app.include_router(auth_router)
app.include_router(history_router)
#serve static files such as CSS,JavaScript,and images
app.mount("/static",StaticFiles(directory="static"),name="static")
#serve the chatbot home page
@app.get("/")
def home():
    return FileResponse("templates/index.html")
@app.get("/register")
def register():
    return FileResponse("templates/register.html")
@app.get("/login")
def login():
    return FileResponse("templates/login.html")