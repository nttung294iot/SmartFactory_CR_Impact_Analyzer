@echo off
setlocal
cd /d %~dp0
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Khong tim thay Python. Hay cai Python 3.11+ va chon Add Python to PATH.
  pause
  exit /b 1
)
python --version
if not exist .venv (
  echo [1/4] Tao virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [2/4] Nang cap pip...
python -m pip install --upgrade pip
echo [3/4] Cai dependencies...
pip install -r requirements.txt
echo [4/4] Khoi tao du lieu demo...
python scripts\initialize_demo.py
echo.
echo HOAN TAT. Chay run_app.bat de mo ung dung.
pause
