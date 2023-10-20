import os
import re
import pandas as pd
# 必要なPdfminer.sixモジュールのクラスをインポート
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO

from common import config

def _do():
  filename = config['files']['meetings']

  # Meetingファイルを読み込む
  if os.path.isfile(filename):
    df = pd.read_excel(filename, index_col=None)
    meetings = df.to_dict(orient='records')
  else:
    print('エラー：' + filename + 'が存在しない。')
    exit(-1)

  for index, meeting in enumerate(meetings):
    print('Converting...:' + str(index + 1) + '/' + str(len(meetings)), end='\r')
    filename = config['folder']['pdf'] + '/' + meeting['No'] + '.pdf'
    # PDFが存在する場合のみ処理
    if os.path.isfile(filename):
      text = _pdf_to_text(filename)
      text = _reform_text(text)

      folder = config['folder']['target'] + '/' + meeting['No'] 
      os.makedirs(folder, exist_ok=True)
      f = open(folder + '/doc.txt', 'w', encoding='utf-8')
      f.write(text)
      f.close()
  
  print('')
  print('Complete to convert')

def _pdf_to_text(pdf_filename: str):
# 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
  fp = open(pdf_filename, 'rb')

  # 出力先をPythonコンソールするためにIOストリームを取得
  outfp = StringIO()

  # 各種テキスト抽出に必要なPdfminer.sixのオブジェクトを取得する処理
  rmgr = PDFResourceManager() # PDFResourceManagerオブジェクトの取得
  lprms = LAParams()          # LAParamsオブジェクトの取得
  device = TextConverter(rmgr, outfp, laparams=lprms)    # TextConverterオブジェクトの取得
  iprtr = PDFPageInterpreter(rmgr, device) # PDFPageInterpreterオブジェクトの取得

  # PDFファイルから1ページずつ解析(テキスト抽出)処理する
  for page in PDFPage.get_pages(fp):
    iprtr.process_page(page)

  text = outfp.getvalue()  # Pythonコンソールへの出力内容を取得

  outfp.close()  # I/Oストリームを閉じる
  device.close() # TextConverterオブジェクトの解放
  fp.close()     #  Fileストリームを閉じる

  return text

def _reform_text(text: str):
  page_filter = config['filter']['page']
  speaker_filter = config['filter']['speaker']
  default_filter = '（.*[議員|氏|議長|委員|大臣|統括官]）'
  pre_erasing_space = config['filter']['pre-erasing-space']


  # 各ページのフッター部分を削除する。
  splitters = re.finditer('', text)
  pages = []
  start = 0
  for splitter in splitters:
    end = splitter.start()
    page = text[start:end]

    # ページ表記を特定し、その直前までを本文として取得する。
    locs = re.finditer(page_filter, page)
    for a in locs:
      loc = a
    new_end = loc.start()
    pages.append(page[:new_end])

    start = splitter.end()
  pages.append(text[end:])
  text = ''.join(pages)

  # 半角スペースを全て除去する
  if pre_erasing_space:
    text = text.replace(' ', '')

  # 話者と会話内容を抽出する。
  check = re.findall(speaker_filter, text)
  if check == []:
    splitters = re.finditer(default_filter, text)
  else:
    splitters = re.finditer(speaker_filter, text)
  speeches = []
  start = 0
  speaker = ''
  for splitter in splitters:
    end = splitter.start()
    speech = erase_space(text[start:end])
    speeches.append(speaker + '　' + speech)

    start = splitter.end()
    speaker = splitter.group().replace('\n', '　')
  speeches.append(erase_space(text[end:]))
  text = '\n'.join(speeches)

  # 半角スペースを全て除去する
  if not pre_erasing_space:
    text = text.replace(' ', '')

  return text

def erase_space(text: str):
  text = re.sub('\n(?!○|〇)', '', text)
  return text
  
if __name__ == '__main__':
  _do()

