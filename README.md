# QueryGPT — Automated SQL Query Generation from Natural Language

A local-first academic micro project that converts natural-language questions to SQLite SELECT queries, validates SQL using SQLGlot, executes read-only queries, displays real results, and persists query history.

## Features
- React + TypeScript + Vite interface with Dashboard, Query Playground, Database Explorer, Schema Viewer, Query History, and Settings.
- FastAPI endpoints and interactive Swagger documentation.
- SQLite academic dataset: 24 fictional students, 7 courses, and 72 enrollments. Seed data is inserted only when the students table is empty.
- Deterministic, explicitly labelled demo SQL generation when no LLM API key is configured.
- Optional OpenAI-compatible chat-completions provider configured only in the backend.
- SQLGlot parsing, single-statement SELECT-only policy, external database qualification rejection, read-only SQLite connection, and bounded result counts.
- CSV export and persistent execution history.
- Pytest backend suite and Windows launcher.

## Requirements
- Windows 10/11
- Python 3.10+ (3.11 recommended)
- Node.js 20+ and npm
- Internet only for installing packages, and optionally for an LLM API provider
- No Docker required

## Windows setup
Open PowerShell in the `QueryGPT` directory.

### 1. Verify tools
```powershell
py --version
node --version
npm --version
```

### 2. Install backend
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
If PowerShell blocks activation, either run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that terminal, or call `.venv\Scripts\python.exe` directly.

### 3. Optional live AI provider
Edit `backend\.env`. Set `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` to a provider that supports the OpenAI-compatible `/chat/completions` API. Keep the key blank to use demo mode. Restart the backend after changing environment settings. Never put the key in frontend files.

### 4. Start backend
From `QueryGPT\backend` with the virtual environment active:
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API health: http://127.0.0.1:8000/api/health  
Swagger: http://127.0.0.1:8000/docs

### 5. Start frontend
Open a second PowerShell terminal:
```powershell
cd QueryGPT\frontend
npm install
npm run dev
```
Open http://localhost:5173

### 6. Start both with the launcher
After both dependency installations are complete, double-click `start.bat` in the project root. It opens separate terminal windows for backend and frontend.

### 7. Run backend tests
From `QueryGPT\backend`:
```powershell
.venv\Scripts\python.exe -m pytest -q
```

### 8. Build frontend for production verification
From `QueryGPT\frontend`:
```powershell
npm run build
```

## Demo prompts
- Show all students
- Find students scoring more than 80 marks
- Count students in each department
- Calculate average marks for each course
- Display the top five students by marks
- Find the highest and lowest marks
- List students enrolled in each course
- Count students in each academic year
- Find courses whose average marks exceed 75

Demo mode is deterministic, not a trained AI model. Unsupported demo prompts return a clear error rather than fabricated SQL or data. For open-ended natural-language generation, configure a compatible LLM provider.

## API overview
See [docs/API.md](docs/API.md) and Swagger at `/docs`.

## Data and security notes
- Database file: `backend/data/querygpt.db` by default. The `.env` file can override `DATABASE_PATH`.
- Sample records are fictional.
- Generated SQL is validated before execution; execute endpoints only permit parsed read-only SELECT statements and apply a row limit.
- SQLite read-only connections are used for query execution. This is a local student project, not a hardened multi-user production service.
- Keep the backend bound to localhost. Do not expose it to an untrusted network.
- SQL query timeouts and maximum rows are configured in `backend/.env`; SQLite's progress handler provides a best-effort interruption mechanism.

## Troubleshooting
- **`py` not recognized:** install Python from python.org and enable the PATH option; reopen PowerShell.
- **`npm` not recognized:** install Node.js LTS and reopen the terminal.
- **Port 8000 in use:** stop the other service or use another port and update the frontend API base URL in `frontend/src/services/api.ts`.
- **Frontend cannot connect:** ensure backend terminal is running and `/api/health` responds.
- **PowerShell activation blocked:** use the process-scoped execution-policy command above or invoke `.venv\Scripts\python.exe` directly.
- **LLM provider errors:** verify base URL, model identifier, key, network, and provider API compatibility. Remove the key and restart for demo mode.
- **Need a clean sample database:** stop the backend, back up then delete `backend/data/querygpt.db`; it will be recreated on next start. This removes local history and any edited records.
