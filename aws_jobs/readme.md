# AWS Batch Jobs 
- Good example: https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/ 
- Setting parameters: https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html#parameters 
- Python example: https://stackoverflow.com/questions/62906304/can-i-map-parameters-passed-to-a-docker-image-to-env-variables-in-python 
- https://stackoverflow.com/questions/56452964/aws-batch-how-to-access-aws-batch-environment-variables-within-python-script-r 
- https://fredhutch.github.io/aws-batch-at-hutch-docs/


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