import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./cred.json"

from fastapi import FastAPI
from routes.events import router as events_router
from routes.healthcheck import router as healthcheck_router
from routes.sockets import router as sockets_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(healthcheck_router)
app.include_router(sockets_router)
