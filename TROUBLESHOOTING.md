# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. Docker Not Found

**Symptom**: `docker: The term 'docker' is not recognized`

**Solution**:
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop (wait for whale icon to be steady)
3. Restart your terminal/PowerShell
4. Verify: `docker --version`

---

### 2. Containers Not Starting

**Symptom**: `docker ps` shows no containers or containers keep restarting

**Solution A - Check Docker Desktop**:
- Open Docker Desktop
- Ensure it's fully started (not "Starting...")
- Check Settings → Resources → Give Docker 4GB+ memory

**Solution B - View Logs**:
```bash
docker compose logs -f
```
Look for specific error messages.

**Solution C - Clean Restart**:
```bash
docker compose down -v
docker compose up -d --build
```

---

### 3. Port Already in Use

**Symptom**: `Error: port is already allocated` or `address already in use`

**Solution**:
```bash
# Stop all containers
docker compose down

# Check what's using the port (example for 8080)
netstat -ano | findstr :8080

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Restart containers
docker compose up -d --build
```

---

### 4. Streamlit Shows "Services Down"

**Symptom**: Red banner "Docker containers not running"

**Checklist**:
1. ✅ Docker Desktop is running
2. ✅ Wait 60 seconds after `docker compose up`
3. ✅ Check containers: `docker ps` (should show 4 containers)
4. ✅ Test manually:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:9090/-/ready
   ```

**If still failing**:
```bash
# Check service health
python check-docker.py

# View container logs
docker compose logs faulty-app
docker compose logs prometheus
docker compose logs loki

# Restart specific service
docker compose restart faulty-app
```

---

### 5. Agent Fails with API Error

**Symptom**: "Agent execution failed" or "API key invalid"

**Solution**:
1. Get free Groq API key: https://console.groq.com/
2. Update `agents.py`:
   ```python
   llm = ChatGroq(
       model="llama-3.1-70b-versatile",
       api_key="gsk_YOUR_ACTUAL_KEY_HERE",  # Replace this!
       temperature=0.1
   )
   ```
3. Restart Streamlit

---

### 6. Metrics Show "N/A"

**Symptom**: All metrics display "N/A" instead of values

**Cause**: Prometheus not receiving metrics from faulty-app

**Solution**:
```bash
# Check if faulty-app is exposing metrics
curl http://localhost:8080/metrics

# Should show Prometheus format metrics like:
# app_heap_usage_bytes 50000000

# If not, restart faulty-app
docker compose restart faulty-app

# Wait 10 seconds, then check Prometheus
# Open: http://localhost:9090/targets
# Status should be "UP" for faulty-app
```

---

### 7. Memory Leak Injection Not Working

**Symptom**: Click "Inject Memory Leak" but metrics don't change

**Solution**:
```bash
# Test injection manually
curl http://localhost:8080/inject/memory-leak

# Should return: {"fault": "memory_leak", "status": "injected"}

# Check metrics after 10 seconds
curl http://localhost:8080/metrics | findstr heap

# Should show increasing heap_usage_bytes

# If not working, check faulty-app logs
docker compose logs faulty-app
```

---

### 8. Slow Container Startup

**Symptom**: Containers take 5+ minutes to start

**Causes & Solutions**:

**Slow Docker Desktop**:
- Settings → Resources → Increase CPU/Memory
- Disable unnecessary startup apps

**Slow Image Download**:
- First time pulls Prometheus, Loki, Grafana images (~500MB)
- Wait patiently or use faster internet

**Windows Defender Scanning**:
- Add Docker folder to exclusions
- Settings → Virus & threat protection → Exclusions

---

### 9. Python Package Errors

**Symptom**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Reinstall all dependencies
pip install -r requriments.txt --force-reinstall

# If specific package fails, install individually
pip install crewai
pip install langchain-groq
pip install streamlit
pip install requests
pip install prometheus-api-client
```

---

### 10. Grafana Not Accessible

**Symptom**: http://localhost:3000 not loading

**Solution**:
```bash
# Check if Grafana container is running
docker ps | findstr grafana

# View Grafana logs
docker compose logs grafana

# Restart Grafana
docker compose restart grafana

# Wait 30 seconds, then access:
# http://localhost:3000
# Login: admin / admin
```

---

## Diagnostic Commands

### Check Everything
```bash
# Service health
python check-docker.py

# Container status
docker ps

# All logs
docker compose logs

# Specific service logs
docker compose logs faulty-app
docker compose logs prometheus
```

### Test Services Manually
```bash
# Faulty app
curl http://localhost:8080/health
curl http://localhost:8080/metrics

# Prometheus
curl http://localhost:9090/-/ready
# Open: http://localhost:9090/targets

# Loki
curl http://localhost:3100/ready

# Grafana
# Open: http://localhost:3000
```

### Clean Slate
```bash
# Nuclear option - remove everything and start fresh
docker compose down -v
docker system prune -a --volumes
docker compose up -d --build
```

---

## Still Having Issues?

1. **Check Docker Desktop logs**: Settings → Troubleshoot → View logs
2. **Check Windows Event Viewer**: Look for Docker-related errors
3. **Verify system requirements**:
   - Windows 10/11 Pro, Enterprise, or Education
   - WSL 2 enabled (for Docker Desktop)
   - Virtualization enabled in BIOS
4. **Try Docker without compose**:
   ```bash
   docker run -d -p 8080:8080 python:3.11-slim
   ```
   If this fails, Docker installation is broken.

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Docker not found | Install Docker Desktop |
| Containers not starting | `docker compose down && docker compose up -d --build` |
| Port in use | `docker compose down` then retry |
| Services down in UI | Wait 60s, run `python check-docker.py` |
| API error | Update Groq key in `agents.py` |
| Metrics N/A | Check http://localhost:9090/targets |
| Slow startup | Give Docker more resources in settings |

---

## Getting Help

If none of these solutions work:

1. Run diagnostics:
   ```bash
   docker compose logs > logs.txt
   python check-docker.py > health.txt
   ```

2. Check the logs for specific error messages

3. Search the error message online (often Docker-specific issues)

4. Ensure your system meets Docker Desktop requirements
