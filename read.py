import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

from common import config

# メインルーチン：変更の有無をフラグで返す
def _do():
  os.makedirs(config['folder']['work'], exist_ok=True)
  filename = config['files']['meetings']

  # 過去ファイルを読み込む
  if os.path.isfile(filename):
    df = pd.read_excel(filename, index_col=None)
    exist = df.to_dict(orient='records')
  else:
    exist = []

  # インターネットから読み込む
  meetings = _get_meeting_list()

  if _compare(exist, meetings):
    flgNoChange = True
  else:
    flgNoChange = False
    df = pd.DataFrame(meetings)
    df.to_excel(filename, header=True, index=False)
    # PDFファイルを読み込む
    _download_pdf(meetings)

  return flgNoChange

# インターネットから会議情報を読み込む
def _get_meeting_list():
  url        = config['internet']['url']
  tag        = config['table']['tag']
  type       = config['table']['type']
  col_kaisu  = int(config['table']['kaisu'])
  col_date   = int(config['table']['date'])
  col_giji   = int(config['table']['giji'])
  col_minute = int(config['table']['minutes'])
  col_other  = int(config['table']['other'])

  session = requests.Session()
  res = session.get(url, verify=True)
  res.encoding = res.apparent_encoding
  soup = BeautifulSoup(res.content, 'html.parser', from_encoding=res.encoding)

  table = soup.find('table', class_ = tag)
  rows = table.find_all('tr')

  meetings = []
  for row in rows:
    cols = row.find_all('td')
    if cols == []:
      continue
    if type == 0:
      kaisu = cols[col_kaisu]
      str_kaisu = kaisu.get_text()

      date_ = cols[col_date]
      str_date  = date_.get_text()
    elif type == 1:
      header_in_row = row.find('th')
      kaisu = header_in_row
      str_kaisu = kaisu.get_text()
      loc = str_kaisu.find('回')
      str_kaisu = str_kaisu[:loc+1]

      date_ = cols[col_date]
      str_date  = date_.get_text()
    elif type == 2:
      header_in_row = row.find('th')
      for i in header_in_row.select("br"):
        i.replace_with("@")
      text_in_header = header_in_row.get_text()
      loc = text_in_header.find('@')
      str_kaisu = text_in_header[:loc].strip()
      str_date = text_in_header[loc:].strip().replace('@','')
    
    str_date = str_date.replace('_x000D_', '').replace('\n', '').strip()
    siryo = cols[col_giji].find('a')
    yousi = cols[col_minute].find('a')
    other = cols[col_other].find('a')

    meetings.append({
      'No'      : str_kaisu,
      'date'    : str_date,
      'doc_url' : _get_url(siryo),
      'summary' : _get_url(yousi),
      'other'  : _get_url(other),
    })

  session.close()

  return meetings

# サイト上のURLアドレスを相対パスから絶対パスに変換する
def _get_url(tag):
  base     = config['internet']['base']
  if tag != None:
    rep = tag.get('href')
    if not rep.startswith('http'):
      rep = base + rep
  else:
    rep = '（現時点で未公開）'
  return rep

# 会議体のリストをローカルとインターネットから新しく取得したものを比較する
def _compare(existone, newone):

  e_len = len(existone)
  n_len = len(newone)

  if e_len != n_len:
    return False
  
  for index, exist in enumerate(existone):
    if exist != newone[index]:
      return False
    
  return True

# PDFをダウンロードする
def _download_pdf(meetings):
  folder = config['folder']['pdf']
  os.makedirs(folder, exist_ok=True)

  session = requests.Session()
  for meeting in meetings:
    url = meeting['summary']
    # サマリーページが設定されている場合のみに処理を行う
    if 'http' in url:
      doc = session.get(url, verify=True)

      f = open(folder+ '/' + meeting['No'] + '.pdf', 'wb')
      f.write(doc.content)
      f.close()

  session.close()

if __name__ == '__main__':

  flgNoChange = _do()

  if flgNoChange:
    print('変更はありません')
    exit(0)
  else:
    print('変更あります。更新しました')
    exit(9)
