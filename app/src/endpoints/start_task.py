import json
from uuid import UUID
from pydantic import BaseModel
from typing import Union

from fastapi import APIRouter

from worker import celery
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime

#APIRouter creates path operations for item module
router = APIRouter(
    prefix="/start-task",
    tags=["start-task"],
    responses={404: {"description": "Not found"}},
)

cred = credentials.Certificate("digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json")
fs_app = firebase_admin.initialize_app(cred, name='fs_app')
fs_db = firestore.client(app=fs_app)

class Item_PostTask(BaseModel):
    user_uuid: str
    input_string: str


@router.post("/")
async def create_item(item: Item_PostTask):
    task_name = "hello.task"
    user_uuid = item.user_uuid
    task = celery.send_task(task_name, args=[item.input_string])
    currentDateTime = datetime.now()
    ## try to send to firestore
    doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(task.id)
    dataToSend = {u'task_id': task.id, u'input_param': item.input_string, u'task_status': u'pending', u'task_result': u'', u'task_error': u'', u'task_created_at': currentDateTime}
    doc_ref.set(dataToSend)
    return dict(id=task.id, url='localhost:5000/check_task/{}'.format(task.id))

