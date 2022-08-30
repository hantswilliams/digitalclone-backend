import boto3

session = boto3.Session(profile_name='biovirtua', region_name='us-east-1')
awsBatch = session.client('batch')
response = awsBatch.list_jobs(
    jobQueue='testing_que',
    jobStatus='SUCCEEDED',
    maxResults=100
)

response['jobSummaryList']

for i in response['jobSummaryList']:
    print(i['jobArn'])
