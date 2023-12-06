import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file(file_name, bucket, object_name=None, extra_args = {}):
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        with open(file_name, 'rb') as data:
            response = s3_client.upload_fileobj(data, bucket, object_name, ExtraArgs=extra_args)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
    
def download_file(bucket, key , file_name):
    s3 = boto3.client('s3')
    print(bucket)
    s3.download_file(Bucket=bucket, Key=key, Filename= file_name)
  
   
def resize_image(file_name, new_name):
    from PIL import Image
    im = Image.open(file_name)
    resized_im = im.resize((round(im.size[0]*0.5), round(im.size[1]*0.5)))
    resized_im.save(new_name)
    
def verify_image(bucket, file_key):
    s3 = boto3.client('s3')
    try:
        metadata = s3.head_object(Bucket=bucket, Key=file_key)['Metadata']["modified"]
        return int(metadata)
    except Exception as e:
        print(e)
        return False