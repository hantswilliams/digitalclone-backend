# Slim backend for digital clone
- Original repo for this: https://github.com/jitendrasinghiitg/docker-fastapi-celery/issues 
- My FORKED version for this: https://github.com/hantswilliams/docker-fastapi-celery 

## Quick run with app/fastAPI only
- go into /app folder and do: 
  - `uvicorn main:app --reload`

## Docker deployment 
- If doing locally, I shade to increase/change my system parameters to: memory swap: 2.5gb, CPUs: 6, Memory: 4gb 
- Will likely run into deployment issues if these settings are not appropaitely set 

## Notes to self: 
- Main additions from default repo are currently: 
  - Integration with Firestore for backing up logs 
  - When connecting to firestore using firebase-admin, will need to download the .json key file that has a structure like this that is inside the /app folder `digital-clone-saas-firebase-adminsdk-8s7c6-35294053d3.json`: 

```
{
  "type": "",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": ""
}
```

  - In app/main.py, would need to insert in the new .json key file (`nameofproject-firebase-admin.json`) and also then be sure to exclude it in the local .gitignore file, or perhaps change this to be a .env file in the future and put it there 


## Original content below this line: 

For FASTAPI i have used docker container from :
https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker

### Run on local machine
Install docker and docker-compose
###### Run entire app with one command 
```
sh local_env_up.sh
```
###### content of local_env_up.sh
```
sudo docker-compose -f docker-compose.yml up --scale worker=2 --build
```
- can add on the `-d` if want to detach terminal from above