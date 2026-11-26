@echo off
setlocal
python -X utf8 "%~dp0studio_server.py" serve %*
if errorlevel 1 pause
