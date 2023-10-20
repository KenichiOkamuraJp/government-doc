import boto3
from dotenv import load_dotenv
if __name__ == '__main__':
  load_dotenv()
  client = boto3.client('s3')
  bucket = 'data.polyarchy.net'
  client.upload_file('index.html', bucket, 'government-meetings/index.html', ExtraArgs={'ContentType': 'text/html' })