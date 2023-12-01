import boto3
import json
import s3utils
import sys
from decouple import config

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
            filename = key.split('/')[-1]
            message_id =  message['Messages'][0]['MessageId']
            print(message_id,bucket_name, key, receipt_handle)
            s3utils.download_file(bucket_name, key, 'image.jpg')
            print('Imagen Recibida')
            s3utils.resize_image('image.jpg','new.jpg')
            print('imagen transformada')
            s3utils.upload_file('new.jpg', bucket_name, f'modified/{filename}',  extra_args={'ACL': 'public-read', "Metadata": {"modified": "True"}}) 
            print('imagen almacenada')
            client.delete_message( QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )
            print('mensaje eliminado')
        except Exception as e:
            print(e)
            client.delete_message( QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )