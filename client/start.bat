@echo off
rem Lance le client en mode console (logs visibles). Ctrl+C pour quitter.
cd /d "%~dp0"
".venv\Scripts\python.exe" presence.py %*
