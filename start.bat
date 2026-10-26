@echo off
echo ========================================================
echo Starting Verity App...
echo ========================================================

:: 1. Check if Docker daemon is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker daemon is not running. Starting Docker Desktop...
    start "" "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
    echo Waiting for Docker daemon to initialize...
    :wait_docker
    timeout /t 3 /nobreak >nul
    docker info >nul 2>&1
    if %ERRORLEVEL% NEQ 0 goto wait_docker
    echo Docker is ready!
)

:: 2. Ensure Database container is running
docker start private-resume-db-old >nul 2>&1

:: 3. Start Backend & Frontend via Docker Compose
echo Starting application containers...
docker compose up -d

echo ========================================================
echo Verity is UP and RUNNING!
echo ========================================================
echo Frontend: http://localhost:5174
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ========================================================
pause
