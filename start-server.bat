@echo off
cd /d "C:\Users\dell\Desktop\Zaynor backend\backend"
echo Starting ZAYNOR Backend Server...
echo.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
