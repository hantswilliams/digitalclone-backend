# Slim backend for digital clone
- Original repo for this: https://github.com/jitendrasinghiitg/docker-fastapi-celery/issues 
- My FORKED version for this: https://github.com/hantswilliams/docker-fastapi-celery 

## Docker deployment 
- If doing locally, I shade to increase/change my system parameters to: memory swap: 2.5gb, CPUs: 6, Memory: 4gb 
- Will likely run into deployment issues if these settings are not appropaitely set 

## Notes to self: 
- Main additions from default repo are currently: 
  - Integration with Firestore for backing up REDIS logs 
  - When connecting to firestore using firebase-admin, will need to download the .json key file that has a structure like this: 

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

It starts a webservice with rest api and listens for messages at localhost:5000

#### Test over REST api

```bash
curl -X POST \
  http://localhost:5000/task_hello_world/ \
  -H 'content-type: application/json' \
  -d '{ "name":"world" }'
```
**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 59
Access-Control-Allow-Origin: *

{
    "id":"a86327b8-2d9b-470d-96a9-a27ad87e2c49",
    "url":"localhost:5000/check_task/a86327b8-2d9b-470d-96a9-a27ad87e2c49"
}
```
and on hitting above url using curl
```
curl -X GET \
  localhost:5000/check_task/a86327b8-2d9b-470d-96a9-a27ad87e2c49

```
we get status of the task ,and on completion it will return the final output of api

when task is in PROGRESS state we get:
```
{
  "status": "PROGRESS",
  "result": {
    "done": 12,
    "total": 60
  },
  "task_id": "954886f1-f625-4076-9851-e7b77bae1ffb"
}
```
when task is in Completed state we get:
```
{
  "status": "SUCCESS",
  "result": {
    "result": "hello world"
  },
  "task_id": "954886f1-f625-4076-9851-e7b77bae1ffb"
}
```

when task is in FAILURE state we get:
```
{
  "status": "FAILURE",
  "result": {
    "exc_type": "ZeroDivisionError",
    "exc_message": [
      "Traceback (most recent call last):",
      "  File \"/celery_tasks/tasks.py\", line 15, in hello_world",
      "    k = 1 / 0",
      "ZeroDivisionError: division by zero",
      ""
    ]
  },
  "date_done": "2020-08-26T11:34:24.179067",
  "task_id": "060229d0-7905-46fa-9082-641581f3e944"
}
```
FAILURE state can be reproduced :
```
curl -X POST \
  http://localhost:5000/task_hello_world \
  -H 'content-type: application/json' \
  -d '{
	"name":"error"	
}'
```
