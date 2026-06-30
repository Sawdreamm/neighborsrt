@echo off
setlocal
cd /d "%~dp0"
set DEST=%USERPROFILE%\.codex\skills\neighborsrt
if not exist "%USERPROFILE%\.codex\skills" mkdir "%USERPROFILE%\.codex\skills"
if exist "%DEST%" rmdir /s /q "%DEST%"
xcopy /E /I /Y "skill" "%DEST%"
echo.
echo Installed NeighborSRT skill to:
echo %DEST%
echo.
echo Optional dependencies for local web:
echo   winget install Gyan.FFmpeg
echo   py -3 -m pip install -U openai-whisper pythainlp
echo.
pause
