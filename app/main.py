import json
from uuid import UUID
from pydantic import BaseModel
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.api import router as api_router

from worker import celery
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:5555",
    "https://localhost:5555",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)