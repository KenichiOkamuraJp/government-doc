import os
import boto3
import pandas as pd
from dotenv import load_dotenv

from common import config

def upload(records):

  load_dotenv()
  client = boto3.client('s3')
  bucket = 'data.polyarchy.net'

  local = config['folder']['html'] +'/'
  folder = 'government-meetings/' + config['folder']['work'] +'/'

  client.upload_file(local + 'index.html', bucket, folder + 'index.html', ExtraArgs={'ContentType': 'text/html' })

  for index, record in enumerate(records):
    filename = local + record['No'] + '.html'
    Key = folder + record['No'] + '.html'
    client.upload_file(filename, bucket, Key, ExtraArgs={'ContentType': 'text/html' })
    print('Progress:' + str(int((index + 1)*100/len(records))) + '%', end='\r')

if __name__ == '__main__':
  japanese_file = config['files']['output-jp']

  # アウトプットファイルを読み込む
  if os.path.isfile(japanese_file):
    df = pd.read_excel(japanese_file, index_col=None)
    records = df.to_dict(orient='records')
  else:
    print('エラー：' + japanese_file + 'が存在しない。')
    exit(-1)

  upload(records)
