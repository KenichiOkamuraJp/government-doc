@echo off
echo **** step1 read ****
python read.py %1
if %ERRORLEVEL%==0 (
  exit /b
) else (
  echo **** step2 convert ****
  python convert.py %1
  echo **** step3 summarize ****
  python summarize.py %1
  echo **** step4 build ****
  python build.py %1
  echo **** step5 deploy ****
  python deploy.py %1
)
