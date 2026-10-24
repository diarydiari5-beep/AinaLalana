@echo off
cd /d "%~dp0"

echo ============================================
echo  AinaWeb - Lancement du serveur
echo ============================================


if not exist "frontend-react\dist\index.html" (
    echo [INFO] Build React introuvable. Construction en cours...
    cd frontend-react
    if not exist "node_modules" (
        echo [INFO] Installation des dependances npm...
        call npm install
    )
    call npm run build
    cd ..
    echo [OK] Build termine.
)

echo [INFO] Demarrage du serveur sur http://localhost:5000
echo [INFO] Appuie sur Ctrl+C pour arreter
echo ============================================
python backend_api.py
