import json
from uuid import UUID
from pydantic import BaseModel
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

cred = credentials.Certificate("digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json")
fs_app = firebase_admin.initialize_app(cred, name='fs_app')
fs_db = firestore.client(app=fs_app)

class Item_PostTask(BaseModel):
    user_uuid: str
    input_string: str

class Item_PostTask_Video1(BaseModel):
    user_uuid: str
    image_url: str
    audio_url: str
    image_name: str
    audio_name: str

class Item_GetTask(BaseModel):
    user_uuid: str
    task_uuid: str

@app.post("/start-task/")
async def create_item(item: Item_PostTask):
    task_name = "hello.task"
    user_uuid = item.user_uuid
    task = celery.send_task(task_name, args=[item.input_string])
    currentDateTime = datetime.now()
    ## try to send to firestore
    doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(task.id)
    dataToSend = {u'task_id': task.id, u'input_param': item.input_string, u'task_status': u'pending', u'task_result': u'', u'task_error': u'', u'task_created_at': currentDateTime}
    doc_ref.set(dataToSend)
    return dict(id=task.id, userid=item.user_uuid, url='localhost:5000/check_task/' + user_uuid + '/{}'.format(task.id))

@app.post("/start-task/video1/")
async def create_item(item: Item_PostTask_Video1):
    task_name = "video1.task"
    user_uuid = item.user_uuid
    task = celery.send_task(task_name, args=[item.user_uuid, item.image_url, item.audio_url, item.image_name, item.audio_name])
    currentDateTime = datetime.now()
    ## try to send to firestore
    doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(task.id)
    dataToSend = {u'task_id': task.id, u'input_param': 
            {u'image_url': item.image_url, u'audio_url': item.audio_url, u'audio_name': item.audio_name, u'image_name': item.image_name}, 
        u'task_status': u'pending', u'task_result': u'', u'task_error': u'', u'task_created_at': currentDateTime}
    doc_ref.set(dataToSend)
    return dict(id=task.id, userid=item.user_uuid, url='localhost:5000/check_task/' + user_uuid + '/{}'.format(task.id))

# check task status by user_uuid and task_uuid and return result
@app.get("/check_task/{user_uuid}/{task_uuid}")
async def check_task(user_uuid, task_uuid):
    user_uuid = user_uuid
    id = task_uuid
    task = celery.AsyncResult(id)

    if task.state == 'SUCCESS':
        taskFinishTime = task.date_done
    else:
        taskFinishTime = None

    if task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.result,
            'task_id': id,
            'task_finished_at': taskFinishTime
        }

        taskid = id
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(taskid)
        dataToSend = {u'task_id': taskid, u'task_status': task.state, u'task_result': task.result, u'task_error': task.info, u'task_finished_at': taskFinishTime}
        doc_ref.update(dataToSend)   

    elif task.state == 'FAILURE':
        response = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)).decode('utf-8'))

        del response['children']
        del response['traceback']

        taskid = id
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(taskid)
        dataToSend = {u'task_id': taskid, u'task_status': task.state, u'task_result': task.result, u'task_error': task.info, u'task_finished_at': taskFinishTime}
        doc_ref.update(dataToSend)    

    else:
        response = {
            'status': task.state,
            'result': task.info,
            'task_id': id,
            'task_finished_at': '-'
        }

        taskid = id
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(taskid)
        dataToSend = {u'task_id': taskid, u'task_status': task.state, u'task_result': task.result, u'task_error': task.info, u'task_finished_at': taskFinishTime}
        doc_ref.update(dataToSend)  

    return response


