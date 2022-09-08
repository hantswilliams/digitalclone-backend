import json
from random import random
import uuid
from pydantic import BaseModel
from typing import Union
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from worker import celery
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import boto3

from datetime import datetime

import os
from dotenv import load_dotenv, dotenv_values

config = dotenv_values(".env")

load_dotenv()

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

session = boto3.Session(aws_access_key_id=config['AWS_ACCESS_KEY'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],region_name='us-east-1')
awsBatch = session.client('batch')

class Item_PostTask(BaseModel):
    user_uuid: str
    input_string: str

class Item_PostTask_Video1(BaseModel):
    user_uuid: str
    image_url: str
    audio_url: str
    image_name: str
    audio_name: str

class Item_PostTask_VideoA1_AWS(BaseModel):
    user_uuid: str
    image_url: str
    audio_url: str
    image_name: str
    audio_name: str
    output_name: str

class Item_GetTaskAWS(BaseModel):
    user_uuid: str
    task_uuid: str
    job_arn: str

@app.get("/")
def read_root():
    return {"App": "Digital Clone", "Version": "1.0.0"}
    

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


@app.post("/start-task/aws-batch/video1/")
async def aws_batch_job(item: Item_PostTask_VideoA1_AWS):
    currentDateTime = datetime.now()
    # create a 4 digit random number for the job name from UUID
    job_name = 'fastAPI-' + str(uuid.uuid4().hex[:8])
    # create a job with the name and the job definition
    response = awsBatch.submit_job(
        # jobDefinition='test-run-8', # this should be configured via portal 
        jobDefinition='test-run-9', # this should be configured via portal 
        jobName=job_name,
        # jobQueue='bigboy_que', # this should be configured via portal 
        # jobQueue='budboy_queue', # this should be configured via portal 
        jobQueue='god8gpus', # this should be configured via portal 
        containerOverrides={
            'environment': [
                {
                    'name': 'ENV_USER_UUID',
                    'value': item.user_uuid
                },
                            {
                    'name': 'ENV_IMAGE_URL',
                    'value': item.image_url
                },
                {
                    'name': 'ENV_AUDIO_URL',
                    'value': item.audio_url
                },
                {
                    'name': 'ENV_IMAGE_NAME',
                    'value': item.image_name
                },
                {
                    'name': 'ENV_AUDIO_NAME',
                    'value': item.audio_name
                },
                {
                    'name': 'ENV_OUTPUT_NAME',
                    'value': item.output_name
                },
            ]
        },
    )

    # then get the appropriate responses 
    jobarn = response['jobArn']
    jobname = response['jobName']
    jobid = response['jobId']
    jobstartdate = response['ResponseMetadata']['HTTPHeaders']['date']

    ## try to send to firestore
    doc_ref = fs_db.collection('users').document(item.user_uuid).collection('tasks').document(jobid)
    dataToSend = {u'task_id': jobid, u'task_arn': jobarn, u'task_name': jobname, u'input_param': 
            {u'image_url': item.image_url, u'audio_url': item.audio_url, u'audio_name': item.audio_name, u'image_name': item.image_name}, 
        u'task_status': u'pending', u'task_result': u'', u'task_error': u'', u'task_created_at': jobstartdate, u'output_name': item.output_name}
    doc_ref.set(dataToSend)

    started_response = {
            'status': 'started',
            'result': response,
            'task_id': jobid,
            'output_name': item.output_name,
            'task_finished_at': '-'
        }

    return started_response





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




@app.post("/check_aws_batch_task")
async def check_aws_batch_task(item: Item_GetTaskAWS):

    user_uuid = item.user_uuid
    id = item.task_uuid
    jobArn = item.job_arn

    print('jobArn provided: ' + jobArn)
    print('task id provided: ' + id)
    print('user_uuid provided: ' + user_uuid)

    #### Get job status, times 
    response_getstatus = awsBatch.describe_jobs(jobs=[jobArn])
    response_status = response_getstatus['jobs'][0]['status']
    

    
    if response_status == 'SUCCEEDED' or response_status == 'FAILED':
        response_created = response_getstatus['jobs'][0]['createdAt']
        response_started = response_getstatus['jobs'][0]['startedAt'] 
        response_stopped = response_getstatus['jobs'][0]['stoppedAt']
        # convert epoch time to readable time
        response_created_readable = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response_created))
        response_started_readable = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime((response_started/1000)))
        response_stopped_readable = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime((response_stopped/1000)))
        # calculate delta between start and stop time in seconds 
        response_delta = response_stopped - response_started
        response_delta_readable = time.strftime("%H:%M:%S", time.gmtime(response_delta/1000))
        # calculate delta between created and stop time in seconds 
        response_delta_created = response_stopped - response_created
        response_delta_created_readable = time.strftime("%H:%M:%S", time.gmtime(response_delta_created/1000))
        taskFinishTime = response_stopped
    else:
        taskFinishTime = None

    if response_status == 'SUCCEEDED':
        response = {
            'status': 'SUCCEEDED',
            'task_id': id,
            'task_finished_at': taskFinishTime,
            'task_duration': response_delta_readable,
            'task_duration_readable': response_delta_created_readable,
            'response_created_readable': response_created_readable,
            'response_started_readable': response_started_readable,
            'response_stopped_readable': response_stopped_readable
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(id)

        dataToSend = {u'task_status': 'SUCCEEDED', u'task_finished_at': response_stopped_readable, u'task_duration': response_delta_readable, 
            u'task_duration_readable': response_delta_created_readable, u'response_created_readable': response_created_readable, 
            u'response_started_readable': response_started_readable, u'response_stopped_readable': response_stopped_readable}

        doc_ref.update(dataToSend)   

    elif response_status == 'FAILED':
        response = {
            'status': 'FAILED',
            'task_id': id,
            'task_finished_at': '-'
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(id)
        dataToSend = {u'task_status': 'FAILED', u'task_finished_at': response_stopped_readable, u'task_duration': response_delta_readable, 
            u'task_duration_readable': response_delta_created_readable, u'response_created_readable': response_created_readable, 
            u'response_started_readable': response_started_readable, u'response_stopped_readable': response_stopped_readable}
        doc_ref.update(dataToSend)     

    else:
        response = {
            'status': response_status,
            'task_id': id,
            'task_finished_at': '-'
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks').document(id)
        dataToSend = {u'task_status': response_status}
        doc_ref.update(dataToSend)  

    return response







# check task status by user_uuid and task_uuid and return result
@app.get("/check_task/aws-batch/{user_uuid}/{task_uuid}")
async def check_task_awsbatch(user_uuid, task_uuid):

    user_uuid = user_uuid
    id = task_uuid

    print('id provided: ' + id)
    print('user_uuid provided: ' + user_uuid)

    #### Get job status, times 
    response_getstatus = awsBatch.describe_jobs(jobs=[id])
    response_status = response_getstatus['jobs'][0]['status']
    response_created = response_getstatus['jobs'][0]['createdAt']
    response_started = response_getstatus['jobs'][0]['startedAt'] 
    response_stopped = response_getstatus['jobs'][0]['stoppedAt']
    # convert epoch time to readable time
    response_created_readable = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response_created))
    response_started_readable = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime((response_started/1000)))
    response_stopped_readable = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime((response_stopped/1000)))
    # calculate delta between start and stop time in seconds 
    response_delta = response_stopped - response_started
    response_delta_readable = time.strftime("%H:%M:%S", time.gmtime(response_delta/1000))
    # calculate delta between created and stop time in seconds 
    response_delta_created = response_stopped - response_created
    response_delta_created_readable = time.strftime("%H:%M:%S", time.gmtime(response_delta_created/1000))
    
    if response_status == 'SUCCEEDED':
        taskFinishTime = response_stopped
    else:
        taskFinishTime = None

    if response_status == 'SUCCEEDED':
        response = {
            'status': 'SUCCEEDED',
            'task_id': id,
            'task_finished_at': taskFinishTime,
            'task_duration': response_delta_readable,
            'task_duration_readable': response_delta_created_readable,
            'response_created_readable': response_created_readable,
            'response_started_readable': response_started_readable,
            'response_stopped_readable': response_stopped_readable
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks-aws-batch').document(id)
        dataToSend = {u'task_status': 'SUCCEEDED', u'task_finished_at': taskFinishTime, u'task_duration': response_delta_readable, 
            u'task_duration_readable': response_delta_created_readable, u'response_created_readable': response_created_readable, 
            u'response_started_readable': response_started_readable, u'response_stopped_readable': response_stopped_readable}
        doc_ref.update(dataToSend)   

    elif response_status == 'FAILED':
        response = {
            'status': 'FAILED',
            'task_id': id,
            'task_finished_at': '-'
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks-aws-batch').document(id)
        dataToSend = {u'task_status': 'FAILED', u'task_finished_at': taskFinishTime, u'task_duration': response_delta_readable, 
            u'task_duration_readable': response_delta_created_readable, u'response_created_readable': response_created_readable, 
            u'response_started_readable': response_started_readable, u'response_stopped_readable': response_stopped_readable}
        doc_ref.update(dataToSend)     

    else:
        response = {
            'status': response_status,
            'task_id': id,
            'task_finished_at': '-'
        }
        doc_ref = fs_db.collection('users').document(user_uuid).collection('tasks-aws-batch').document(id)
        dataToSend = {u'task_status': response_status}
        doc_ref.update(dataToSend)  

    return response