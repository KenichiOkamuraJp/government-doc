import os
import sys
import yaml

args = sys.argv

if len(args) < 2:
  print('必要引数が不足しています：[会議体名]')
  exit(1)
else:
  if os.path.isfile('configs/' + args[1] + '.yaml'):
    _filename = 'configs/' + args[1] + '.yaml'
  else:
    print('config fileが存在しません')
    exit(1)

  with open(_filename, encoding='utf-8') as file:
    config = yaml.safe_load(file)