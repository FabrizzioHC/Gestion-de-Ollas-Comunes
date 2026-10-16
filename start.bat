@echo off
REM Script para iniciar backend y frontend de Red Comunitaria en Windows

echo.
echo ==========================================
echo Red Comunitaria - Sistema de Inicio
echo ==========================================
echo.

REM Iniciar el backend en una nueva ventana
echo [1/2] Iniciando Backend (Flask)...
cd backend
start "Backend - Red Comunitaria" cmd /k python app.py
timeout /t 2 /nobreak

REM Iniciar el frontend en una nueva ventana
echo [2/2] Iniciando Frontend...
cd ..\frontend
start "Frontend - Red Comunitaria" cmd /k python -m http.server 8000

echo.
echo ==========================================
echo. System iniciado correctamente
echo ==========================================
echo.
echo URLs:
echo   Frontend:  http://localhost:8000
echo   Backend:   http://localhost:5000
echo.
echo Credenciales de prueba:
echo   Admin: admin@redcomunitaria.com / abc123$
echo   Donador: donador@gmail.com / abc123$
echo   Olla: olla@gmail.com / abc123$
echo.
echo Para detener, cierra las ventanas de consola
echo.
pause
