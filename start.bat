@echo off
set ROOT=%~dp0
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
 echo Backend virtual environment not found. Run the setup steps in README.md first.
 pause
 exit /b 1
)
if not exist "%ROOT%frontend\node_modules" (
 echo Frontend dependencies not found. Run npm install inside frontend first.
 pause
 exit /b 1
)
start "QueryGPT Backend" cmd /k "cd /d "%ROOT%backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "QueryGPT Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"
echo QueryGPT is starting. Frontend: http://localhost:5173  API docs: http://127.0.0.1:8000/docs
