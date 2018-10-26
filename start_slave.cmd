@echo off
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "[ Perfang (1 Slave Server) ]" /D "%~dp0" /min "%~dpnx0" %* && exit
chcp 65001
:: mode CON: COLS=40
:: mode CON: LINES=10
mode 40, 10
::
set FLASK_DEBUG=1
set FLASK_APP=server/slave.py
set PYTHONIOENCODING=utf-8
cd "%~dp0"
:: cd ..
set PYTHONPATH=%cd%
:: cd server
(
echo Python Path: %PYTHONPATH%
:: python -m flask run --host=0.0.0.0 --port=5001
python server/slave.py
exit
) >> _slave-server.log 2>&1
