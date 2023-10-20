import os
import pandas as pd
from make_summary import make_summary
from common import config

f = open('apikey', 'r')
apikey = f.read()
f.close()
os.environ["OPENAI_API_KEY"] = apikey

def _do():
  meeting_file = config['files']['meetings']
  output_file  = config['files']['output-jp']

  # Meetingファイルを読み込む
  if os.path.isfile(meeting_file):
    df = pd.read_excel(meeting_file, index_col=None)
    meetings = df.to_dict(orient='records')
  else:
    print('エラー：' + meeting_file + 'が存在しない。')
    exit(-1)

  # 既存のファイルを読み込む
  if os.path.isfile(output_file):
    df = pd.read_excel(output_file, index_col=None)
    exist_records = df.to_dict(orient='records')
  else:
    exist_records = []

  # 既存レコードに一致しないレコードのみを処理対象に含める
  targets = []
  for meeting in meetings:
    name = meeting['No']
    for record in exist_records:
      if record['No'] == name:
        break
    else:
      targets.append(meeting)

  # 新しい処理対象が存在しない場合はFalseを返す
  if targets == []:
    return False

  # 処理対象のレコードについてサマリー処理を行う
  new_records = []
  for index, meeting in enumerate(targets):
    print('Summerizing...:' + str(index + 1) + '/' + str(len(targets)), end='\r')
    name = meeting['No']
    flg, text1, text2, topics = make_summary(name)
    if flg:
      record = {
        'No'      : meeting['No'],
        'date'    : meeting['date'],
        'summary' : text1,
        'topics'  : text2,
        'source'  : meeting['summary']
      }
      for idx, topic in enumerate(topics):
        key1 = 'topic{:0=3}'.format(idx+1)
        key2 = 'answer{:0=3}'.format(idx+1)
        record[key1] = topic['topic']
        record[key2] = topic['answer']
      new_records.append(record)

  new_records.extend(exist_records)
  print('')
  print('Complete to summerize')

  df = pd.DataFrame(new_records)
  df.to_excel(output_file, header=True, index=False)

  return True

if __name__ == '__main__':
  flgNewRecords = _do()

  if flgNewRecords:
    print('変更あり')
  else:
    print('変更なし')

