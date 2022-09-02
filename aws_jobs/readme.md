# AWS Batch Jobs 
- Good example: https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/ 
- Setting parameters: https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html#parameters 
- Python example: https://stackoverflow.com/questions/62906304/can-i-map-parameters-passed-to-a-docker-image-to-env-variables-in-python 
- https://stackoverflow.com/questions/56452964/aws-batch-how-to-access-aws-batch-environment-variables-within-python-script-r 
- https://fredhutch.github.io/aws-batch-at-hutch-docs/



## Instructions for setting up, can set IaaC later: 
- For batch in AWS: 
    1. Compute environment 
    2. Job que environment 
    3. Job definitions 
    4. Jobs 

- Breakdown: 
    1. Compute enviornment is base, it is where everything else sort of runs 
    2. Job que environemnt -> the que for what is up, managing the jobs - so the jobs will need to be assigned a que environment 
    3. Job definitions -> basic outline, here is where you would set the defined parameters like the image container, executation role, and the command that will be execute when the image starts 
    4. Jobs -> this is where you would then submit a new job, based on a job definition, and perhaps update the environment variables (input parameters) for that specific job

- Manditory things to have first setup before trying to start a new job: 
    1. Job definition 
    2. Job que 

- Current setup: 
    1. Build and Push Dockerfile in this subfolder aws_jobs into ECR 
    2. When you push a update, new ECR build, will need to connect ECR image to a new `Job definition` , e.g., you cant try old one 
    3. Job definition settings for how the current image is build: 
        - Command: `python3 test.py` will run the test.py file found in aws_jobs/a2h 
        - Environment variables configuration: `ENV_VAR_1` and `ENV_VAR_2` and examples that could be placed with appropriate values


- Job definition: 
```
{
    "containerProperties": {
.
.
.
        "environment": [
            {
                "name": "BATCH_FILE_S3_URL",
                "value": "s3://my-batch-scripts/myjob.sh"
            },
            {
                "name": "BATCH_FILE_TYPE",
                "value": "script"
            }
        ]
}
```
- In python file
```
S3_URL=os.getenv('BATCH_FILE_S3_URL')
```