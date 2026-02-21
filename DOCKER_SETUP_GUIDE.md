# 🐳 Docker Setup Guide - Step by Step

## Current Status
❌ Docker is NOT installed on your system

## Step-by-Step Installation

### Step 1: Download Docker Desktop (2 minutes)

1. Open your browser and go to:
   ```
   https://www.docker.com/products/docker-desktop/
   ```

2. Click the big blue button: **"Download for Windows"**

3. Wait for the installer to download (~500MB)

---

### Step 2: Install Docker Desktop (5 minutes)

1. **Run the installer** (Docker Desktop Installer.exe)

2. **During installation**:
   - ✅ Check "Use WSL 2 instead of Hyper-V" (recommended)
   - ✅ Check "Add shortcut to desktop"
   - Click "Ok"

3. **Installation will**:
   - Install Docker Engine
   - Install Docker CLI
   - Set up WSL 2 (if needed)
   - May require a restart

4. **If prompted to restart**: Click "Close and restart"

---

### Step 3: Start Docker Desktop (2 minutes)

After restart (or if no restart needed):

1. **Find Docker Desktop**:
   - Look for Docker icon on desktop
   - OR search "Docker Desktop" in Start Menu

2. **Launch Docker Desktop**

3. **Wait for initialization**:
   - You'll see a whale icon in system tray (bottom-right)
   - Icon will animate while starting
   - **Wait until the whale stops animating** (steady icon)
   - This takes 30-60 seconds

4. **Accept terms** if prompted

---

### Step 4: Verify Docker is Running

Open PowerShell (doesn't need to be Administrator) and run:

```powershell
docker --version
```

Should show something like:
```
Docker version 24.0.7, build afdd53b
```

Then check Docker is running:
```powershell
docker ps
```

Should show:
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

(Empty list is fine - it means Docker is running but no containers yet)

---

### Step 5: Start Your SRE Agent Services

Now that Docker is running, start your containers:

```powershell
# Make sure you're in the right folder
cd "C:\Users\Arjun\OneDrive\Desktop\ROBOCOP"

# Start all services
docker compose up -d --build
```

This will:
- Build the faulty-app container
- Download Prometheus, Loki, Grafana images (~500MB first time)
- Start all 4 containers
- Takes 2-3 minutes first time

---

### Step 6: Wait and Verify (1 minute)

Wait 60 seconds for services to initialize, then check:

```powershell
docker ps
```

Should show 4 containers running:
```
CONTAINER ID   IMAGE                    STATUS         PORTS                    NAMES
xxxxx          robocop-faulty-app       Up 30 seconds  0.0.0.0:8080->8080/tcp   robocop-faulty-app-1
xxxxx          prom/prometheus:latest   Up 30 seconds  0.0.0.0:9090->9090/tcp   robocop-prometheus-1
xxxxx          grafana/loki:2.9.0       Up 30 seconds  0.0.0.0:3100->3100/tcp   robocop-loki-1
xxxxx          grafana/grafana:latest   Up 30 seconds  0.0.0.0:3000->3000/tcp   robocop-grafana-1
```

---

### Step 7: Test Services

```powershell
# Test faulty app
curl http://localhost:8080/health

# Should return: {"status":"healthy"}

# Test Prometheus
curl http://localhost:9090/-/ready

# Should return: Prometheus is Ready.
```

OR run the automated checker:
```powershell
python check-docker.py
```

Should show all ✅ green checkmarks.

---

### Step 8: Refresh Streamlit UI

1. Go back to your browser: http://localhost:8501

2. Press **R** key (or click "Rerun" in top-right)

3. You should now see:
   - ✅ "All services running" banner at top
   - Real metric values (not "N/A")
   - Heap Usage: ~50 MB
   - Restarts: 0
   - Latency: ~30 ms
   - All buttons enabled

---

## Troubleshooting

### Issue: "WSL 2 installation is incomplete"

**Solution**:
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart computer
4. Start Docker Desktop again

---

### Issue: "Docker Desktop requires a newer WSL kernel version"

**Solution**:
1. Download WSL update: https://aka.ms/wsl2kernel
2. Install the update
3. Restart Docker Desktop

---

### Issue: "Hardware assisted virtualization is not enabled"

**Solution**:
1. Restart computer
2. Enter BIOS (usually press F2, F10, or Del during boot)
3. Find "Virtualization Technology" or "Intel VT-x" or "AMD-V"
4. Enable it
5. Save and exit BIOS
6. Start Docker Desktop

---

### Issue: Port already in use (8080, 9090, etc.)

**Solution**:
```powershell
# Find what's using the port (example for 8080)
netstat -ano | findstr :8080

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Try starting Docker again
docker compose up -d --build
```

---

### Issue: "docker compose" not recognized

**Solution**:
Your Docker version might use the old syntax. Try:
```powershell
docker-compose up -d --build
```

(Note the hyphen instead of space)

---

### Issue: Containers keep restarting

**Solution**:
```powershell
# Check logs to see what's failing
docker compose logs -f

# Look for error messages
# Common issues:
# - Port conflicts
# - Missing files
# - Memory limits too low
```

---

## Quick Commands Reference

```powershell
# Check Docker version
docker --version

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Start services
docker compose up -d --build

# Stop services
docker compose down

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs faulty-app

# Restart a service
docker compose restart faulty-app

# Remove everything and start fresh
docker compose down -v
docker compose up -d --build
```

---

## System Requirements

Before installing Docker Desktop, ensure:

- ✅ Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
  OR Windows 11 64-bit
- ✅ 4GB RAM minimum (8GB recommended)
- ✅ BIOS-level hardware virtualization enabled
- ✅ WSL 2 feature enabled

To check Windows version:
```powershell
winver
```

---

## After Docker is Running

Once all services are up:

1. **Test the agent**:
   - Go to http://localhost:8501
   - Click "Inject Memory Leak"
   - Click "Launch Autonomous Agent"
   - Watch it work!

2. **Explore services**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)
   - Faulty App: http://localhost:8080/health

3. **Read the docs**:
   - START_HERE.md for overview
   - QUICKSTART.md for detailed guide

---

## Need More Help?

1. **Docker won't install**: Check system requirements above
2. **Docker won't start**: Check TROUBLESHOOTING.md
3. **Containers won't start**: Run `docker compose logs -f` and check errors
4. **Still stuck**: Copy the error message and search online

---

## Summary

1. ❌ Docker not installed → Download from docker.com
2. ⏳ Install Docker Desktop → May require restart
3. ▶️ Start Docker Desktop → Wait for whale icon to be steady
4. ✅ Verify: `docker --version` and `docker ps`
5. 🚀 Start services: `docker compose up -d --build`
6. ⏱️ Wait 60 seconds
7. ✅ Verify: `python check-docker.py`
8. 🎉 Refresh Streamlit and test!

---

**You're almost there! Just need to install Docker and you'll be running in 10 minutes!** 🚀
