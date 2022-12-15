import json
from random import random
import uuid
from pydantic import BaseModel
from typing import Union
import time
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from zipfile import ZipFile

import boto3

from datetime import datetime

import os
from dotenv import load_dotenv, dotenv_values

import pandas as pd
import json

config = dotenv_values(".env")

load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:5555",
    "https://localhost:5555",
    "https://server.appliedhealthinformatics.com",
    "https://clone.appliedhealthinformatics.com"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cred = credentials.Certificate("digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json")
fs_app = firebase_admin.initialize_app(cred, name='fs_app')
fs_db = firestore.client(app=fs_app)
bucket_location = 'digital-clone-saas.appspot.com'
bucket = storage.bucket(bucket_location, app=fs_app)

session = boto3.Session(aws_access_key_id=config['AWS_ACCESS_KEY'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],region_name='us-east-1')
awsBatch = session.client('batch')

# load example sentances
sentances = pd.read_csv('/voiceCloning/sentances/sentances.csv')
sentances['list'] = sentances['list'].astype(str)

class Sentance(BaseModel):
    sentance: str
    list: str

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
    return {"App": "Digital Clone", "Version": "0.0.3"}

### create a endpoint that downloads all audio files in a users firebase storage folder
@app.get("/download-all-audio/{user_uuid}")
def download_audio(user_uuid: str):
    # get all files in the users folder
    blobs = bucket.list_blobs(prefix='user/' + user_uuid + '/voice/')
    audio_files = []
    for blob in blobs:
        print(blob.name)
        if '.wav' in blob.name:
            audio_files.append(blob.name)

    # just keep characters after the final / in the file name
    audio_files_clean = [x.split('/')[-1] for x in audio_files]

    # download the audio files locally in working directory
    for i in audio_files_clean:
        blob = bucket.blob('user/' + user_uuid + '/voice/' + i)
        blob.download_to_filename('app/temp/' + i)

    # use pythons built-in zip to zip all the files in app/temp as zip.zip
    with ZipFile('app/temp/zip.zip', 'w') as zipObj:
        for folderName, filenames in os.walk('app/temp'):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath, filename)

    # return the zip file
    return FileResponse('app/temp/zip.zip', media_type='application/zip', filename='zip.zip')


##### Endpoints related to digital cloning #####
##### Endpoints related to digital cloning #####
##### Endpoints related to digital cloning #####

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

    # ## checking for errors 
    # print('response_getstatus: ' + response_getstatus)
    # print('response_status: ' + response_status)

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




##### Endpoints related to retrieving sentances for voice cloning #####
##### Endpoints related to retrieving sentances for voice cloning #####
##### Endpoints related to retrieving sentances for voice cloning #####

@app.get("/sentances")
async def get_all_sentances():
    # convert the df sentances to dictionary
    df_sentances_dict = sentances.to_dict('records')
    return df_sentances_dict

@app.get("/sentances/list/{sentance_list_id}")
async def get_sentance(sentance_list_id: str):
    # keep only the sentance that matches the sentance_list_id
    df_sentance = sentances[sentances['list'] == sentance_list_id]
    # convert the df sentances to dictionary
    df_sentances_dict = df_sentance.to_dict('records')
    return df_sentances_dict

@app.get("/sentances/list/random/{random_count}")
async def get_random_sentance(random_count: str):
    df_sentance = sentances.sample(int(random_count))
    # convert the df sentances to dictionary
    df_sentances_dict = df_sentance.to_dict('records')
    return df_sentances_dict

