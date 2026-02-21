@echo off
echo Stopping all Docker containers...
docker compose down -v
echo.
echo All services stopped and cleaned up.
pause
