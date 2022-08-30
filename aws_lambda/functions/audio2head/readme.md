# Things to do/remidners:

## note 
- a2h folder should be a sync, or as close to avoid drift of `/celery/funcitons/audio2head` 
- will need to insert in the firebase config file for admin connection 
- will need to download the training tar file, put that into the dockerscript at the beginning, since its big 
    - navigate to proper directory for it `{navigat to folder checkpoints then} wget --no-check-certificate --no-proxy https://nhit-public.s3.us-east-2.amazonaws.com/audio2head.pth.tar` 

- got the ffmpeg oscent install from, os centos: `https://github.com/pulumi/examples/tree/master/aws-ts-lambda-thumbnailer` 

# running locally 
- `docker build -t audio2head .` 
- `docker run -p 9000:8080 audio2head:latest` 
## testing ? 
- `   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'    `
## check out postman for examples
    - user_uuid = `qwbtOiHXETaW0d0HQhm37fRal1B2` 
    - image_name = `hantsCartoon.jpeg` 
    - audio_name =  `1661562484193.wav` 
    - image_url = 'https://firebasestorage.googleapis.com/v0/b/digital-clone-saas.appspot.com/o/user%2FqwbtOiHXETaW0d0HQhm37fRal1B2%2FhantsCartoon.jpeg?alt=media&token=528cc987-6de8-45c9-8b5b-a2247d99d227' 
    - audio_url = `https://firebasestorage.googleapis.com/v0/b/digital-clone-saas.appspot.com/o/user%2FqwbtOiHXETaW0d0HQhm37fRal1B2%2F1661562484193.wav?alt=media&token=0d413ed9-2d97-4ccd-b3c1-f0a815af654b` 
## error messages
- related to build process, 403: `DOCKER_BUILDKIT=0 docker build -t a2h .` 


# deploying 
- created ECR - `audio2head` in hants@biovirtua AWS account 
- build: `docker build -t audio2head .`
- tag: `docker tag audio2head:latest 521663328127.dkr.ecr.us-east-1.amazonaws.com/audio2head:latest`
- push: `docker push 521663328127.dkr.ecr.us-east-1.amazonaws.com/audio2head:latest` 

## testing deployment/production 
- easiest just to use `Function URL` versus setting up api gateway 
- be sure to create a new role, and lock it down, so require IAM key/secret in request since this will be using big instance type
- CORS issues: 
    - expose headers and allow headers: 
        - content-type, accept, special-key, access-control-allow-origin 
    - allow origin: * 
    - allow methods: * 
- then for the frontend, have something like: 
```
      headers: {
        'content-type': 'application/json',
        'accept': 'application/json',
        'access-control-allow-origin': 'http://localhost:3000/dashboard/create',
    }
```
