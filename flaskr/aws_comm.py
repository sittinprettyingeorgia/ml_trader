import logging
import boto3
from botocore.exceptions import ClientError


# communicate with aws s3
def create_bucket(bucket_name, region='us-west-2'):
    try:  # if this fails we may need to switch from boto3.resource to boto3.client
        s3_client = boto3.resource('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

    except ClientError as e:
        logging.error(e)
        return False

    return True


def upload_model(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.resource('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False

    return True


def get_model(bucket, object_name, file_name):
    s3 = boto3.resource('s3')
    s3.download_file(bucket, object_name, file_name)


# communicate with aws dynamodb
def get_dynamo():
    dynamo_client = boto3.resource('dynamodb')
    return dynamo_client
