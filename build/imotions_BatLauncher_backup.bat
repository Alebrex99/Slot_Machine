@echo off
cd /d "%~dp0"
start /wait "" "%~dp0SlotMachine_TEST.exe"
timeout /t 1 /nobreak >nul
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('+{PGDN}')"
