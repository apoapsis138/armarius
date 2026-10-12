@echo off
rem Start the desktop version of Ars Magica Manager (installs its Qt
rem libraries on first run).
cd /d "%~dp0"
uv run --group gui python gui.py
if errorlevel 1 pause
