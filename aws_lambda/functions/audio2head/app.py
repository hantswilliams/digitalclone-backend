from time import sleep
import traceback
import os
import json

# Import Audio2Head model
from create_video import audio2head

# Firebase Admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Import UUID4 to create token
from uuid import uuid4

## connect to firesbase services for storage bucket
cred = credentials.Certificate("digital-clone-saas-firebase-admin-sdk.json")    
firebase_admin.initialize_app(cred, {
    'storageBucket': 'digital-clone-saas.appspot.com'
})
bucket = storage.bucket()

def lambda_handler(event, context):

    print('## EVENT')
    print("Event variables: ", event)
    print(os.environ)
    print("## CONTEXT")
    print("Lambda function ARN:", context.invoked_function_arn)
    print("CloudWatch log stream name:", context.log_stream_name)
    print("CloudWatch log group name:",  context.log_group_name)
    print("Lambda Request ID:", context.aws_request_id)

    lambdaDetails = {
        'invoked_function_arn': context.invoked_function_arn,
        'log_stream_name': context.log_stream_name,
        'log_group_name': context.log_group_name,
        'aws_request_id': context.aws_request_id
    }


    # see if event contains body
    if 'body' in event:
        print('...body found in event, assuming prod event')
        body = json.loads(event['body'])
        user_uuid, image_url, audio_url, image_name, audio_name = body['user_uuid'], body['image_url'], body['audio_url'], body['image_name'], body['audio_name']
    else:
        print('...body not found in event, assuming dev event')
        user_uuid, image_url, audio_url, image_name, audio_name = event['user_uuid'], event['image_url'], event['audio_url'], event['image_name'], event['audio_name']

    
    ## vars assigned
    print('user_uuid: ', user_uuid)
    print('image_url: ', image_url)
    print('audio_url: ', audio_url)
    print('image_name: ', image_name)
    print('audio_name: ', audio_name)

    ## dummy response 
    dummyResponse = {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

    # create a temp directory if one doesn't exist 
    if not os.path.exists('/tmp/' + user_uuid):
        os.makedirs('/tmp/' + user_uuid)

    image_fire_path = 'user/{user_uuid}/{image_name}'.format(user_uuid=user_uuid, image_name=image_name)
    audio_fire_path = 'user/{user_uuid}/{audio_name}'.format(user_uuid=user_uuid, audio_name=audio_name)

    image_local_path = '/tmp/' + user_uuid + '/' + image_name
    audio_local_path = '/tmp/' + user_uuid + '/' + audio_name
    video_local_path = '/tmp/' + user_uuid + '/processed_video1/' 

    print('Firebase image loc:', image_fire_path)
    print('Forebase audio loc:', audio_fire_path)

    # download image and audio from firebase storage and place it in temp directory
    bucket.blob(image_fire_path).download_to_filename(image_local_path)
    bucket.blob(audio_fire_path).download_to_filename(audio_local_path)

    # print out the temp directory and list the files in it 
    print('Temp directory:', '/tmp/' + user_uuid)
    print('Files in temp directory:', os.listdir('/tmp/' + user_uuid))

    # create video from image and audio
    # structure: audiofile, imagefile, model_path, save_path
    mode_path = '/var/task/checkpoints/audio2head.pth.tar'
    audio2head(audio_local_path, image_local_path, mode_path, video_local_path)

    video_fire_path = 'user/{user_uuid}/processed/processed_video1_'.format(user_uuid=user_uuid) + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
    video_local_path_file = video_local_path + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
    bucket.blob(video_fire_path).upload_from_filename(video_local_path_file)
    
    print('Video uploaded to firebase storage')

    # on complete of printing, delete the temp directory and files
    os.system('rm -rf /tmp/' + user_uuid)

    # for i in range(60):
    #     sleep(1)
    #     self.update_state(state='PROGRESS', meta={'done': i, 'total': 60, 'user_uuid': user_uuid, 'image_url': image_url, 'audio_url': audio_url})

    return {"result": "video1_task", "dummyResponse": dummyResponse, "lambdaDetails": lambdaDetails}