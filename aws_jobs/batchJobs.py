import boto3
import time

import os
from dotenv import load_dotenv, dotenv_values

config = dotenv_values(".env")

# session = boto3.Session(profile_name='biovirtua', region_name='us-east-1')
session = boto3.Session(aws_access_key_id=config['AWS_ACCESS_KEY'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'], region_name='us-east-1')
awsBatch = session.client('batch')

# list_jobs 
# create_compute_environment
# create_job_queue
# describe_job_queues
# describe_job_definitions
# describe_jobs
# submit_job
# terminate_job


#### Things to include when creating a new a job: 
# create new job
response = awsBatch.submit_job(
    jobDefinition='test-run-3', # this should be configured via portal 
    jobName='submitted-via-python',
    jobQueue='testing_que', # this should be configured via portal 
    containerOverrides={
        'environment': [
            {
                'name': 'ENV_VAR_1',
                'value': 'from-python1'
            },
                        {
                'name': 'ENV_VAR_2',
                'value': 'from-python2'
            },
        ]
    },
)
# then get the appropriate responses 
jobarn = response['jobArn']
jobname = response['jobName']
jobid = response['jobId']
jobstartdate = response['ResponseMetadata']['HTTPHeaders']['date']
# will then need to save these to firestore with the UUID of the user






#### Get job status, times 
response_getstatus = awsBatch.describe_jobs(jobs=[jobarn])
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






response = awsBatch.list_jobs(
    jobQueue='god8gpus',
    jobStatus='SUCCEEDED',
    maxResults=100
)



response = awsBatch.list_jobs(
    jobQueue='testing_que',
    jobStatus='SUCCEEDED',
    maxResults=100
)

response['jobSummaryList']
for i in response['jobSummaryList']:
    print('jobArn: ', i['jobArn'])
    print('jobName: ', i['jobName'])
