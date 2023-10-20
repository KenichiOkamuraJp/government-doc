import os
import operator
import pandas as pd
import datetime
import mojimoji

NO_DETAIL = '（議事録未公開）'

def getRecords(aConfig):
  meeting_file  = aConfig['files']['meetings']
  japanese_file = aConfig['files']['output-jp']

  # ミーティングファイルを読み込む
  if os.path.isfile(meeting_file):
    df = pd.read_excel(meeting_file, index_col=None)
    meetings = df.to_dict(orient='records')
  else:
    print('エラー：' + meeting_file + 'が存在しない。')
    exit(-1)

  # アウトプットファイルを読み込む
  if os.path.isfile(japanese_file):
    df = pd.read_excel(japanese_file, index_col=None)
    records = df.to_dict(orient='records')
  else:
    print('エラー：' + japanese_file + 'が存在しない。')
    exit(-1)

  new_records = records.copy()
  for meeting in meetings:
    check = meeting['No']
    flgNew = True
    for record in records:
      if record['No'] == check:
        flgNew = False
        break
    if flgNew:
      new_records.append({
        'No'      : meeting['No'],
        'date'    : meeting['date'],
        'summary' : NO_DETAIL,
        'topics'  : NO_DETAIL,
        'source'  : NO_DETAIL
      })

  # 開催日時をdatetime型に変換
  result = []
  for rec in new_records:
    aDate = toDate(rec['date'])
    result.append({
      'No'      : rec['No'],
      'date'    : rec['date'],
      'summary' : rec['summary'],
      'topics'  : rec['topics'],
      'source'  : rec['source'],
      'index'   : aDate
    })

  result = sorted(result, key=operator.itemgetter('index'), reverse=True)
  return result

def toDate(dateStr: str):
  dateStr = mojimoji.zen_to_han(dateStr)
  dateStr = dateStr.replace('　','').replace(' ', '')

  nen   = dateStr.find('年')
  gatsu = dateStr.find('月')
  pi    = dateStr.find('日')
  if '令和' in dateStr:
    year = 2018
    strYear = dateStr[2:nen]
  elif '平成' in dateStr:
    year = 1988
    strYear = dateStr[2:nen]
  elif '昭和' in dateStr:
    year = 1925
    strYear = dateStr[2:nen]
  else:
    year = 0
    strYear = dateStr[:nen]
  strMonth  = dateStr[nen+1:gatsu]
  strDay    = dateStr[gatsu+1:pi]
  numYear  = year + int(strYear)
  numMonth = int(strMonth)
  numDay   = int(strDay)

  return datetime.date(numYear, numMonth, numDay)