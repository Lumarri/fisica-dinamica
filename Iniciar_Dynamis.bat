@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>&1
    if errorlevel 1 (
        echo Instala Python 3.11 o posterior con el lanzador de Python para Windows.
        echo Despues vuelve a abrir este archivo.
        pause
        exit /b 1
    )
    py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 11))"
    if errorlevel 1 (
        echo Se requiere Python 3.11 o posterior.
        pause
        exit /b 1
    )
    py -3 -m venv .venv
    if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -c "import PySide6, matplotlib, numpy, scipy, pandas" >nul 2>&1
if errorlevel 1 (
    echo Instalando las dependencias del programa. Esta primera vez necesita Internet.
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto error
exit /b 0
:error
echo No se pudo iniciar Dynamis. Revisa el mensaje anterior o consulta README.md.
pause
exit /b 1
