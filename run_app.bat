@echo off
setlocal
cd /d %~dp0

if not exist .venv\Scripts\activate.bat (
  echo Chua cai dat. Dang chay setup.bat...
  call setup.bat
)

call .venv\Scripts\activate.bat

rem Stop an older Streamlit instance on port 8501 so the browser does not show stale UI.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
  taskkill /PID %%a /F >nul 2>&1
)

streamlit cache clear >nul 2>&1
start "" http://localhost:8501
streamlit run app.py --server.port 8501
pause