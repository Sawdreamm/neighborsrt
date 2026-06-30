@echo off
setlocal
cd /d "%~dp0"

echo NeighborSRT full installer for Windows
echo ====================================
echo.

where winget >nul 2>nul
if errorlevel 1 (
  echo winget is required for automatic installation.
  echo Install "App Installer" from Microsoft Store, then run this again.
  pause
  exit /b 1
)

where py >nul 2>nul
if errorlevel 1 (
  echo Installing Python 3.12...
  winget install -e --id Python.Python.3.12
) else (
  echo Python launcher found.
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo Installing ffmpeg...
  winget install -e --id Gyan.FFmpeg
) else (
  echo ffmpeg found.
)

echo.
echo Installing Python packages...
py -3 -m pip install -U openai-whisper pythainlp
if errorlevel 1 (
  echo pip install failed.
  pause
  exit /b 1
)

echo.
echo Installing Codex skill...
set DEST=%USERPROFILE%\.codex\skills\neighborsrt
if not exist "%USERPROFILE%\.codex\skills" mkdir "%USERPROFILE%\.codex\skills"
if exist "%DEST%" rmdir /s /q "%DEST%"
xcopy /E /I /Y "skill" "%DEST%"

echo.
set /p DOWNLOAD_MODEL="Download Whisper large-v3 now? This is about 3GB. [y/N] "
if /I "%DOWNLOAD_MODEL%"=="Y" (
  py -3 -c "import whisper; print('Downloading/loading large-v3. This may take a while...'); whisper.load_model('large-v3'); print('large-v3 is ready.')"
)

echo.
echo Done.
echo Start local web with:
echo   start_windows.bat
pause
