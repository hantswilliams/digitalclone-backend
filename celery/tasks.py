from time import sleep
import traceback
import os

# Celery
from celery import current_task
from celery import states
from celery.exceptions import Ignore
from worker import celery

# Firebase Admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Import UUID4 to create token
from uuid import uuid4

# Specific functions
from functions.audio2head.create_video import audio2head


## connect to firesbase services for storage bucket
cred = credentials.Certificate("digital-clone-saas-firebase-admin-sdk.json")    
firebase_admin.initialize_app(cred, {
    'storageBucket': 'digital-clone-saas.appspot.com'
})
bucket = storage.bucket()


@celery.task(name='hello.task', bind=True)
def hello_world(self, name):
    try:
        if name == 'error':
            k = 1 / 0
        for i in range(60):
            sleep(1)
            self.update_state(state='PROGRESS', meta={'done': i, 'total': 60})
        return {"result": "hello {}".format(str(name))}
    except Exception as ex:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(ex).__name__,
                'exc_message': traceback.format_exc().split('\n')
            })
        raise ex


@celery.task(name='video1.task', bind=True)
def video1_task(self, user_uuid, image_url, audio_url, image_name, audio_name):

    try:

        self.update_state(state='PROGRESS', meta={'done': 'beginning to process request', 'total': 60, 'user_uuid': user_uuid, 'image_url': image_url, 'audio_url': audio_url})

        # create a temp directory if one doesn't exist 
        if not os.path.exists('/tmp/' + user_uuid):
            os.makedirs('/tmp/' + user_uuid)

        image_fire_path = 'user/{user_uuid}/{image_name}'.format(user_uuid=user_uuid, image_name=image_name)
        audio_fire_path = 'user/{user_uuid}/{audio_name}'.format(user_uuid=user_uuid, audio_name=audio_name)

        image_local_path = '/tmp/' + user_uuid + '/' + image_name
        audio_local_path = '/tmp/' + user_uuid + '/' + audio_name
        video_local_path = '/tmp/' + user_uuid + '/processed_video1/' # + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'

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
        mode_path = '/celery_tasks/functions/audio2head/checkpoints/audio2head.pth.tar'
        audio2head(audio_local_path, image_local_path, mode_path, video_local_path)

        # # upload video to firebase storage
        # # Create new token
        # new_token = uuid4()
        # # Create new dictionary with the metadata
        # metadata  = {"firebaseStorageDownloadTokens": new_token}

        video_fire_path = 'user/{user_uuid}/processed/processed_video1_'.format(user_uuid=user_uuid) + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
        video_local_path_file = video_local_path + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
        bucket.blob(video_fire_path).upload_from_filename(video_local_path_file)
        
        print('Video uploaded to firebase storage')

        # on complete of printing, delete the temp directory and files
        os.system('rm -rf /tmp/' + user_uuid)

        self.update_state(state='SUCCESS', meta={'done': 'video created', 'total': 60, 'user_uuid': user_uuid, 'image_url': image_url, 'audio_url': audio_url})

        # for i in range(60):
        #     sleep(1)
        #     self.update_state(state='PROGRESS', meta={'done': i, 'total': 60, 'user_uuid': user_uuid, 'image_url': image_url, 'audio_url': audio_url})

        return {"result": "video1_task"}
    
    except Exception as ex:

        print('Exception:', ex)

        self.update_state(
            state=states.FAILURE,
            meta={
                'done': 'error',
                'total': 'something went wrong'
            })
        raise ex

