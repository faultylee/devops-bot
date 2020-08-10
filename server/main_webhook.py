import json
import os
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import boto3

API_GATEWAY_ROOT = 'API_GATEWAY_ID.execute-api.ap-southeast-1.amazonaws.com'
DDB_TABLE_NAME = 'devops-bot-client'

session = boto3.session.Session()

"""
Allowing forwarder from another account to invoke this lambda
aws lambda add-permission \
    --function-name {THIS_FUNCTION_NAME} \
    --statement-id cross_account_invoke_by_forwarder \
    --action lambda:InvokeFunction \
    --principal "{FORWARDER_AWS_ACCOUNT_ID}"

"""


def lambda_handler(event, context):
    auth = AWSRequestsAuth(aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=os.environ[
                               'AWS_SECRET_ACCESS_KEY'],
                           aws_token=os.environ['AWS_SESSION_TOKEN'],
                           aws_host=API_GATEWAY_ROOT,
                           aws_region='ap-southeast-1',
                           aws_service='execute-api')
    dynamodb = session.client('dynamodb')
    for item in dynamodb.scan(TableName=DDB_TABLE_NAME).get('Items'):
        client_id = item.get('client-id').get('S')
        data = json.dumps(event)
        print('POST: ',
              f'https://{API_GATEWAY_ROOT}/default/@connections/{client_id}',
              data)
        requests.post(
            f'https://{API_GATEWAY_ROOT}/default/@connections/{client_id}',
            auth=auth, data=data)
    return {
        "statusCode": 200,
    }
