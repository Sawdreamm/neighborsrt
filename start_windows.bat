@echo off
setlocal
cd /d "%~dp0"
echo Starting NeighborSRT Local Web...
echo Open http://127.0.0.1:8765 in your browser.
start "" "http://127.0.0.1:8765"
py -3 app\server.py
if errorlevel 1 (
  echo.
  echo Failed to start with py -3. Trying python...
  python app\server.py
)
pause
