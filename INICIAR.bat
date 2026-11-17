@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
if errorlevel 1 goto carpeta_error
title Red Comunitaria - Inicio rapido
echo ==================================================
echo   RED COMUNITARIA - INICIO RAPIDO
echo ==================================================
echo.
if not exist "run.py" goto carpeta_error
if not exist "iniciar.py" goto carpeta_error
if not exist "requirements.txt" goto carpeta_error
if exist "venv\Scripts\python.exe" goto usar_venv
if exist ".venv\Scripts\python.exe" goto usar_dotvenv
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if not errorlevel 1 goto crear_con_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if not errorlevel 1 goto crear_con_python
echo No se encontro Python 3.9 o superior.
echo Instala Python para Windows y vuelve a abrir este archivo.
goto fin_error

:crear_con_py
echo Creando el entorno virtual...
py -3 -m venv "venv"
if errorlevel 1 goto entorno_error
goto usar_venv

:crear_con_python
echo Creando el entorno virtual...
python -m venv "venv"
if errorlevel 1 goto entorno_error
goto usar_venv

:usar_venv
"venv\Scripts\python.exe" "iniciar.py"
if errorlevel 1 goto fin_error
goto fin

:usar_dotvenv
".venv\Scripts\python.exe" "iniciar.py"
if errorlevel 1 goto fin_error
goto fin

:entorno_error
echo No se pudo crear el entorno virtual.
echo Extrae el proyecto en una carpeta donde puedas guardar archivos.
goto fin_error

:carpeta_error
echo Extrae el ZIP completo antes de ejecutar INICIAR.bat.
echo El archivo debe estar junto a run.py e iniciar.py.
goto fin_error

:fin_error
echo.
echo El proyecto no pudo iniciar. Revisa el mensaje anterior.
echo Para la base de datos, solo debes editar .env.
pause
exit /b 1

:fin
echo.
echo Proyecto detenido.
pause
exit /b 0
