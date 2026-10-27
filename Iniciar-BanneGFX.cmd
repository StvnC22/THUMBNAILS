@echo off
title BanneGFX - Servidor local
cd /d "%~dp0"
start "" "http://127.0.0.1:5173/"
"C:\Users\Stvn\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd" run dev -- --host 127.0.0.1
pause
