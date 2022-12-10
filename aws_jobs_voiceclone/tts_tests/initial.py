from time import sleep
import traceback
import os
import json

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

def voiceClone():

    user_uuid=os.getenv('ENV_USER_UUID')
    image_url=os.getenv('ENV_IMAGE_URL')
    audio_url=os.getenv('ENV_AUDIO_URL')
    image_name=os.getenv('ENV_IMAGE_NAME')
    audio_name=os.getenv('ENV_AUDIO_NAME')
    output_name=os.getenv('ENV_OUTPUT_NAME')

    ## vars assigned
    print('user_uuid: ', user_uuid)
    print('image_url: ', image_url)
    print('audio_url: ', audio_url)
    print('image_name: ', image_name)
    print('audio_name: ', audio_name)
    print('output_name: ', output_name)

    ## remove special characters from outputname
    output_name_clean = output_name.replace('[^A-Za-z0-9]+', '_')

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

    # # create video from image and audio
    # # structure: audiofile, imagefile, model_path, save_path
    # mode_path = '/a2h/checkpoints/audio2head.pth.tar'

    # run the actual model here
    # audio2head(audio_local_path, image_local_path, mode_path, video_local_path)

    # # video_fire_path = 'user/{user_uuid}/processed/awsbatch_processed_video1_'.format(user_uuid=user_uuid) + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
    # video_fire_path = 'user/{user_uuid}/processed/awsbatch_processed_video1_'.format(user_uuid=user_uuid) + output_name_clean + '.mp4'
    # video_local_path_file = video_local_path + image_name[:-4] + '_' + audio_name[:-4] + '.mp4'
    # bucket.blob(video_fire_path).upload_from_filename(video_local_path_file)
    
    print('Model uploaded to firebase storage')

    # on complete of printing, delete the temp directory and files
    os.system('rm -rf /tmp/' + user_uuid)

    return {"succesfully processed": True}


if __name__ == '__main__':
    voiceClone()