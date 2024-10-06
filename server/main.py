from fastapi import FastAPI, WebSocket
import socketio
from routes.sockets import router as socket_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./cred.json"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(socket_router)


