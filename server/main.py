import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./cred.json"

from fastapi import FastAPI
from routes.sockets import router as socket_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(socket_router)
