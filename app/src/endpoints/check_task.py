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
    prefix="/check_task",
    tags=["Product"],
    responses={404: {"description": "Not found"}},
)

class Item_GetTask(BaseModel):
    user_uuid: str
    task_uuid: str

cred = credentials.Certificate("digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json")
fs_app2= firebase_admin.initialize_app(cred, name='fs_app2')
fs_db2 = firestore.client(app=fs_app2)

@router.get("/{user_uuid}/{task_uuid}")
async def check_task(user_uuid, task_uuid):

    user_uuid = user_uuid
    id = task_uuid
    task = celery.AsyncResult(id)

    # print('task: ', task['date_done'])

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
        doc_ref = fs_db2.collection('users').document(user_uuid).collection('tasks').document(taskid)
        dataToSend = {u'task_id': taskid, u'task_status': task.state, u'task_result': task.result, u'task_error': task.info, u'task_finished_at': taskFinishTime}
        doc_ref.update(dataToSend)   

    elif task.state == 'FAILURE':
        response = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)).decode('utf-8'))

        del response['children']
        del response['traceback']

        taskid = id
        doc_ref = fs_db2.collection('users').document(user_uuid).collection('tasks').document(taskid)
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