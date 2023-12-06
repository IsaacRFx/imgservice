import boto3
import json
import s3utils
import sys
from decouple import config
import requests

QUEUE_URL = config('SQS_URL')

client = boto3.client('sqs')

stop = len(sys.argv) > 1 and sys.argv[1] == 'stop'

run = True

while run:
    if stop: # El parámetro stop detiene el script despues de un loop
        run = False
    message = client.receive_message(QueueUrl=QUEUE_URL,
                    WaitTimeSeconds=2,
                    )
    if message and 'Messages' in message and message['Messages']:
        try:
            receipt_handle = message['Messages'][0]['ReceiptHandle']
            body =  json.loads(message['Messages'][0]['Body'])
            bucket_name = body['Records'][0]['s3']['bucket']['name']
            key = body['Records'][0]['s3']['object']['key']
            if key:
                is_modified_file = s3utils.verify_image(bucket_name, key)
                if not is_modified_file:
                    filename = key.split('/')[-1]
                    message_id =  message['Messages'][0]['MessageId']
                    print(message_id,bucket_name, key, receipt_handle)
                    s3utils.download_file(bucket_name, key, 'image.jpg')
                    print(f'Received Image: {filename}')
                    s3utils.resize_image('image.jpg','new.jpg')
                    print('Transforming Image...')
                    new_key=f'{filename.split(".")[0]}-mod.jpg'
                    s3utils.upload_file('new.jpg', bucket_name, new_key,  extra_args={'ACL': 'public-read',"ContentType":"image/jpeg", "Metadata": {"modified": "1"}}) 
                    print(f'New image: {new_key}')
                    body={"object_key":f"{new_key}"}
                    r = requests.post(f"{config('API_URL')}/api/files/webhook/", json=body)
                    print(r.json())
            client.delete_message( QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )
            print('Message deleted')
        except Exception as e:
            print(e)
            client.delete_message( QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )