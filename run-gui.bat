@echo off
rem Start the desktop version of Armarius (installs its Qt
rem libraries on first run). The window opens alone: this console
rem closes behind it, so the taskbar shows only Armarius's own icon.
cd /d "%~dp0"
if not defined UV_PROJECT_ENVIRONMENT set "UV_PROJECT_ENVIRONMENT=%~dp0.venv"
uv sync --inexact --group gui --quiet
if errorlevel 1 (
    pause
    exit /b 1
)
start "" "%UV_PROJECT_ENVIRONMENT%\Scripts\pythonw.exe" gui.py
