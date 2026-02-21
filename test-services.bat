@echo off
echo ========================================
echo  Testing SRE Agent Services
echo ========================================
echo.

echo Testing Faulty App (port 8080)...
curl -s http://localhost:8080/health
if errorlevel 1 (
    echo FAILED - Faulty app not responding
) else (
    echo OK
)
echo.

echo Testing Prometheus (port 9090)...
curl -s http://localhost:9090/-/ready
if errorlevel 1 (
    echo FAILED - Prometheus not responding
) else (
    echo OK
)
echo.

echo Testing Loki (port 3100)...
curl -s http://localhost:3100/ready
if errorlevel 1 (
    echo FAILED - Loki not responding
) else (
    echo OK
)
echo.

echo Testing Grafana (port 3000)...
curl -s http://localhost:3000/api/health
if errorlevel 1 (
    echo FAILED - Grafana not responding
) else (
    echo OK
)
echo.

echo ========================================
echo Running Python health check...
echo ========================================
python check-docker.py
echo.

pause
