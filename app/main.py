import json
from pydantic import BaseModel
from fastapi import FastAPI
from worker import celery
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = FastAPI()

cred = credentials.Certificate("digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json")
fs_app = firebase_admin.initialize_app(cred, name='fs_app')
fs_db = firestore.client(app=fs_app)

class Item_PostTask(BaseModel):
    input_string: str
    user_uuid: str

class Item_GetTask(BaseModel):
    user_uuid: str
    task_uuid: str

@app.post("/task_hello_world/")
async def create_item(item: Item_PostTask):
    task_name = "hello.task"
    user_uuid = item.user_uuid
    task = celery.send_task(task_name, args=[item.input_string])
    ## try to send to firestore
    doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(task.id)
    dataToSend = {u'task_id': task.id, u'input_param': item.input_string, u'task_status': u'pending', u'task_result': u'', u'task_error': u''}
    doc_ref.set(dataToSend)
    return dict(id=task.id, url='localhost:5000/check_task/{}'.format(task.id))

    


# @app.get("/check_task/{id}")
@app.get("/check_task/")
def check_task(item: Item_GetTask):
    user_uuid = item.user_uuid
    id = item.task_uuid
    task = celery.AsyncResult(id)
    if task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.result,
            'task_id': id
        }
    elif task.state == 'FAILURE':
        response = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)).decode('utf-8'))
        del response['children']
        del response['traceback']
    else:
        response = {
            'status': task.state,
            'result': task.info,
            'task_id': id
        }

    taskid = id
    doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(taskid)
    dataToSend = {u'task_id': taskid, u'task_status': task.state, u'task_result': task.result, u'task_error': task.info}
    doc_ref.update(dataToSend)


    return response
