@echo off
setlocal
cd /d "%~dp0"
.venv\Scripts\python ui\app.py
pause
