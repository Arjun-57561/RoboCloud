@echo off
echo ========================================
echo  SRE Agent - Startup Script
echo ========================================
echo.

echo [1/4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found!
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo Docker found!
echo.

echo [2/4] Starting Docker containers...
docker compose up -d --build
if errorlevel 1 (
    echo ERROR: Failed to start containers!
    echo Try: docker compose down
    echo Then run this script again.
    pause
    exit /b 1
)
echo.

echo [3/4] Waiting for services to initialize (60 seconds)...
timeout /t 60 /nobreak >nul
echo.

echo [4/4] Checking service health...
python check-docker.py
if errorlevel 1 (
    echo.
    echo WARNING: Some services may not be ready yet.
    echo Wait another 30 seconds and check manually:
    echo   python check-docker.py
    echo.
)

echo.
echo ========================================
echo  Ready to launch!
echo ========================================
echo.
echo Run: streamlit run app.py
echo Then open: http://localhost:8501
echo.
pause
