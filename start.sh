#!/bin/bash

# Script para iniciar backend y frontend de Red Comunitaria

echo "=========================================="
echo "Red Comunitaria - Sistema de Inicio"
echo "=========================================="

# Iniciar el backend
echo ""
echo "[1/2] Iniciando Backend (Flask)..."
cd backend
python app.py &
BACKEND_PID=$!
echo "Backend iniciado con PID $BACKEND_PID"
echo "API disponible en http://localhost:5000"

# Dar tiempo al backend para iniciar
sleep 2

# Iniciar el frontend
echo ""
echo "[2/2] Iniciando Frontend..."
cd ../frontend
python -m http.server 8000 &
FRONTEND_PID=$!
echo "Frontend iniciado con PID $FRONTEND_PID"
echo "Frontend disponible en http://localhost:8000"

echo ""
echo "=========================================="
echo "✓ Sistema iniciado correctamente"
echo "=========================================="
echo ""
echo "URLs:"
echo "  Frontend:  http://localhost:8000"
echo "  Backend:   http://localhost:5000"
echo ""
echo "Credenciales de prueba:"
echo "  Admin: admin@redcomunitaria.com / abc123$"
echo "  Donador: donador@gmail.com / abc123$"
echo "  Olla: olla@gmail.com / abc123$"
echo ""
echo "Para detener, presiona Ctrl+C"
echo ""

# Mantener los procesos corriendo
wait $BACKEND_PID $FRONTEND_PID
