import os

from fastapi import FastAPI
from routes.sockets import router as socket_router
from fastapi.middleware.cors import CORSMiddleware

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
