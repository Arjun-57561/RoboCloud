@echo off
echo ========================================
echo  SRE Agent - Setup Verification
echo ========================================
echo.

echo [1/5] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker NOT installed
    echo.
    echo Please install Docker Desktop:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo See DOCKER_SETUP_GUIDE.md for detailed instructions.
    pause
    exit /b 1
) else (
    docker --version
    echo ✅ Docker is installed
)
echo.

echo [2/5] Checking if Docker is running...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is NOT running
    echo.
    echo Please start Docker Desktop from Start Menu
    echo Wait for the whale icon in system tray to stop animating
    echo Then run this script again.
    pause
    exit /b 1
) else (
    echo ✅ Docker is running
)
echo.

echo [3/5] Checking required files...
set MISSING=0

if not exist "docker-compose.yml" (
    echo ❌ Missing: docker-compose.yml
    set MISSING=1
)
if not exist "prometheus.yml" (
    echo ❌ Missing: prometheus.yml
    set MISSING=1
)
if not exist "loki-config.yml" (
    echo ❌ Missing: loki-config.yml
    set MISSING=1
)
if not exist "faulty-app\Dockerfile" (
    echo ❌ Missing: faulty-app\Dockerfile
    set MISSING=1
)
if not exist "faulty-app\app.py" (
    echo ❌ Missing: faulty-app\app.py
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo Some required files are missing!
    pause
    exit /b 1
) else (
    echo ✅ All required files present
)
echo.

echo [4/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python NOT installed
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python is installed
)
echo.

echo [5/5] Checking Python dependencies...
python -c "import crewai, streamlit, requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python dependencies NOT installed
    echo.
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
) else (
    echo ✅ Python dependencies installed
)
echo.

echo ========================================
echo  ✅ ALL CHECKS PASSED!
echo ========================================
echo.
echo Your system is ready to run the SRE Agent.
echo.
echo Next steps:
echo   1. Start Docker services: docker compose up -d --build
echo   2. Wait 60 seconds
echo   3. Verify: python check-docker.py
echo   4. Launch UI: streamlit run app.py
echo.
pause
