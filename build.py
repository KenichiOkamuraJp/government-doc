import os
from typing import List
from common import config
from tools import getRecords, NO_DETAIL

def make(records: List):
  html_folder = config['folder']['html']
  os.makedirs(html_folder, exist_ok=True)

  # データの取得
  html_contents, details = make_contents(records)

  # 全体サマリー
  html_pre = '''
    <!DOCTYPE html>
    <html lang="ja">
      <head>
        <meta charset="UTF-8">
        <title>{0}</title>
      </head>
      <body>
  '''.format(config['name'])

  html_title = '<h2>{0} 議事サマリー一覧</h2>'.format(config['name']) + \
    '<h3><a href="../index.html">政府会議体一覧に戻る</a></h3>'

  html_header = '''
        <hr>
        <table border="2">
          <thead>
            <tr>
              <th width="5%">開催回数</th>
              <th width="10%">開催日時</th>
              <th width="45%">サマリー</th>
              <th width="30%">トピック</th>
              <th width="5%">詳細情報</th>
              <th width="5%">原文書</th>
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

  html = html_pre + html_title + html_header + html_contents + html_post
  f = open(html_folder + '/index.html', 'w', encoding='utf-8')
  f.write(html)
  f.close()

  # 各回サマリー
  for detail in details:
    rec = detail['record']
    html_detail = detail['html']
    html_pre = '''
      <!DOCTYPE html>
      <html lang="ja">
        <head>
          <meta charset="UTF-8">
          <title>{0} {1}</title>
        </head>
        <body>
    '''.format(config['name'], rec['No'])

    html_title = '<h2>{1}{0} 議事サマリー一覧</h2>'.format(rec['No'], config['name']) + \
      '<h3>{0}開催　　<a href="./index.html">一覧に戻る</a>　　'.format(rec['date']) + \
      '<a href="{0}" target="_blank">原文書を参照する</a></h3>'.format(rec['source'])

    html_header = '''
          <hr>
          <h3>サマリー</h3>
          <h4>{0}</h4>
          <hr>
          <table border="2">
            <thead>
              <tr>
                <th width="33%">トピック</th>
                <th width="66%">詳細</th>
              </tr>
            </thead>
            <tbody>
    '''.format(rec['summary'])

    html_post = '''
            </tbody>
          </table>
        </body>
      </html>
    '''

    html2 = html_pre + html_title + html_header + html_detail + html_post
    f = open(html_folder + '/' + rec['No'] + '.html', 'w', encoding='utf-8')
    f.write(html2)
    f.close()

def make_contents(records: List):
  html = ''
  details = []
  for record in records:

    if record['summary'] == NO_DETAIL:
      html = html + \
        '<tr><td>' + record['No'] + '</td>' + \
        '<td>' + record['date'] + '</td>' + \
        '<td>' + record['summary'] + '</td>' + \
        '<td>' + record['topics'] + '</td>' + \
        '<td>' + record['topics'] + '</td>' + \
        '<td>' + record['source'] + '</td></tr>'

    else:

      html = html + \
        '<tr><td>' + record['No'] + '</td>' + \
        '<td>' + record['date'] + '</td>' + \
        '<td>' + record['summary'] + '</td>' + \
        '<td>' + str(record['topics']).replace('\n', '<br>') + '</td>' + \
        '<td><a href="./' + record['No'] + '.html">詳細</a></td>' + \
        '<td><a href="' + record['source'] + '" target="_blank">原文書</a></td></tr>'
    
      detail_html = ''
      for key in record.keys():
        if key in ['No', 'date', 'summary', 'topics', 'source']:
          continue
        if type(record[key]) == str:
          if 'topic' in key:
            detail_html = detail_html + '<tr><td>' + record[key] + '</td>'
          if 'answer' in key:
            detail_html = detail_html + '<td>' + record[key] + '</td></tr>'
      details.append({
        'record' : record,
        'html'   : detail_html
      })
    
  return html, details

if __name__ == '__main__':
  result = getRecords(config)
  make(result)