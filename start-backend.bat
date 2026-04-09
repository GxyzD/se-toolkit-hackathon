@echo off
echo Starting Study Group Matcher Backend...
echo.

cd /d "%~dp0backend"

echo Testing imports...
..\..\.venv\Scripts\python -c "from app.main import app; print('OK')" || (
    echo ERROR: Failed to import app
    pause
    exit /b 1
)

echo.
echo Starting server on http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.

..\..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
