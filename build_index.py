import os
import yaml
import pandas as pd

from tools import getRecords

def get_meetings():

  # 会議体のリストとコンフィグを読込
  df = pd.read_csv('kaigi.csv', header=0)
  meetings = df.to_dict(orient='records')

  _meetings = []
  for meeting in meetings:
    if os.path.isfile('configs/' + meeting['code'] + '.yaml'):
      _filename = 'configs/' + meeting['code'] + '.yaml'
    else:
      print('Config fileが存在しません : ' + meeting['code'])
      exit(1)

    with open(_filename, encoding='utf-8') as file:
      config = yaml.safe_load(file)
      _meetings.append({
        'code' : meeting['code'],
        'name' : meeting['name'],
        'config' : config
      })

  return _meetings

def get_contents(config):
  records = getRecords(config)
  if len(records) > 0:
    latest = records[0]
  else:
    latest = None
  return latest

def make_html(records):
  # HTMLの作成
  html = ''
  for record in records:
    html = html + '  <tr>' + \
      '<td>' + str(record['Id']) + '</td>' + \
      '<td><a href="' + record['Link'] + '">' + record['Name'] + '</a></td>' + \
      '<td>' + record['No'] + '</td>' + \
      '<td>' + record['Date'] + '</td>' + \
      '<td>' + record['Summary'] + '</td>' + \
      '</tr>\n'
  return html

def build(body: str):
  
  html_pre = '''
    <!DOCTYPE html>
    <html lang="ja">
      <head>
        <meta charset="UTF-8">
        <title>{0}</title>
      </head>
      <body>
  '''.format('政府会議体')

  html_title = '<h2>政府会議体一覧</h2>'

  html_header = '''
        <hr>
        <table border="2">
          <thead>
            <tr>
              <th width="5%">ID</th>
              <th width="10%">会議名</th>
              <th width="5%">開催回数</th>
              <th width="5%">開催日時</th>
              <th width="45%">サマリー</th>
            </tr>
          </thead>
          <tbody>
  '''

  html_post = '''
          </tbody>
        </table>
      </body>
    </html>
  '''

  return html_pre + html_title + html_header + body + html_post

if __name__ == '__main__':
  meetings = get_meetings()
  records = []
  for index, meeting in enumerate(meetings):
    latest = get_contents(meeting['config'])
    records.append({
      'Id'      : index + 1,
      'Name'    : meeting['name'],
      'No'      : latest['No'],
      'Date'    : latest['index'].strftime('%Y/%m/%d'),
      'Summary' : latest['summary'],
      'Topics'  : latest['topics'],
      'Link'    : meeting['code'] + '/index.html'
    })
  body = make_html(records)
  html = build(body)

  f = open('index.html', 'w', encoding='utf-8')
  f.write(html)
  f.close()
