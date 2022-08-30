import json
import boto3
from pprint import pprint
def lambda_handler(event, context):
    # TODO implement
    client = boto3.client("ec2")
    status = client.describe_instance_status(IncludeAllInstances = True)
    #pprint(status)
    for i in status["InstanceStatuses"]:
        print("AvailabilityZone :", i["AvailabilityZone"])
        print("InstanceId :", i["InstanceId"])
        print("InstanceState :", i["InstanceState"])
        print("InstanceStatus", i["InstanceStatus"])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }