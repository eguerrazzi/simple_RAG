@echo off
echo ========================================
echo Avvio Sistema RAG Completo
echo ========================================
echo.

REM Credenziali Admin Panel (modificare qui se necessario)
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123

echo [1/4] Avvio RAG API Server (porta 8000)...
start "RAG API Server" cmd /c "python api_server.py"

echo [2/4] Avvio Admin Panel (porta 8080)...
start "Admin Panel" cmd /c "python admin_panel.py"

echo Attendo 5 secondi per l'avvio dei server...
timeout /t 5 /nobreak > nul

echo.
echo [3/4] Verifica Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ATTENZIONE: Docker non e' in esecuzione!
    echo Avvia Docker Desktop e riprova.
    echo ========================================
    echo.
    echo Nel frattempo puoi usare:
    echo   - Admin Panel: http://localhost:8080
    echo   - API Server:  http://localhost:8000
    echo.
    pause
    exit /b 1
)

echo [4/4] Avvio Open WebUI con Docker (porta 3000)...
docker stop open-webui 2>nul
docker rm open-webui 2>nul
docker run -d --name open-webui ^
    -p 3000:8080 ^
    -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 ^
    -e OPENAI_API_KEY=not-needed ^
    -e WEBUI_AUTH=true ^
    -e DEFAULT_MODELS=rag-gemini ^
    -v open-webui-data:/app/backend/data ^
    --add-host=host.docker.internal:host-gateway ^
    --restart unless-stopped ^
    ghcr.io/open-webui/open-webui:main

echo.
echo Attendo avvio Open WebUI...
timeout /t 10 /nobreak > nul

echo.
echo ========================================
echo        SISTEMA RAG PRONTO!
echo ========================================
echo.
echo SERVIZI ATTIVI:
echo   - Open WebUI (Chat):    http://localhost:3000
echo   - Admin Panel (Upload): http://localhost:8080
echo   - RAG API Server:       http://localhost:8000
echo.
echo CREDENZIALI ADMIN PANEL:
echo   Username: %ADMIN_USERNAME%
echo   Password: %ADMIN_PASSWORD%
echo.
echo ISTRUZIONI:
echo   1. Vai su Admin Panel per caricare documenti
echo   2. Clicca "Reindicizza" dopo l'upload
echo   3. Riavvia api_server.py per applicare
echo   4. Usa Open WebUI per chattare
echo.
echo Per fermare tutto:
echo   - Chiudi le finestre "RAG API Server" e "Admin Panel"
echo   - Esegui: docker stop open-webui
echo.
pause
