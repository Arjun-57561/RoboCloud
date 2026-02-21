# 📦 Installation Guide

## Prerequisites

### 1. Docker Desktop (Required)

**Download**: https://www.docker.com/products/docker-desktop/

**System Requirements**:
- Windows 10/11 64-bit (Pro, Enterprise, or Education)
- WSL 2 feature enabled
- Virtualization enabled in BIOS
- 4GB RAM minimum (8GB recommended)

**Installation Steps**:
1. Download Docker Desktop installer
2. Run installer (may require restart)
3. Start Docker Desktop
4. Wait for "Docker Desktop is running" status
5. Verify: Open PowerShell and run `docker --version`

**Enable WSL 2** (if not already):
```powershell
wsl --install
```
Restart computer after installation.

---

### 2. Python 3.11+ (Required)

**Check if installed**:
```bash
python --version
```

**If not installed**:
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Restart terminal after installation

---

### 3. Groq API Key (Required)

**Get free key**:
1. Visit: https://console.groq.com/
2. Sign up (free)
3. Go to API Keys section
4. Create new key
5. Copy the key (starts with `gsk_`)

---

## Installation Steps

### Step 1: Install Python Dependencies

Open PowerShell in the project folder:

```bash
pip install -r requirements.txt
```

**If you get errors**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

---

### Step 2: Configure Groq API Key

Edit `agents.py` and replace the API key:

```python
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key="gsk_YOUR_ACTUAL_KEY_HERE",  # Paste your key here
    temperature=0.1
)
```

---

### Step 3: Start Docker Services

**Option A - Use Batch Script** (Recommended):
```bash
start.bat
```
This will:
- Check Docker is installed
- Start all containers
- Wait for services to initialize
- Verify health

**Option B - Manual**:
```bash
docker compose up -d --build
```
Wait 60 seconds for services to start.

---

### Step 4: Verify Installation

Run the health check:
```bash
python check-docker.py
```

Should show:
```
✅ Faulty App: Running
✅ Prometheus: Running
✅ Loki: Running

✅ All services are running!
```

**If services are down**: See TROUBLESHOOTING.md

---

### Step 5: Launch Application

```bash
streamlit run app.py
```

Browser should open automatically to http://localhost:8501

**If browser doesn't open**: Manually visit http://localhost:8501

---

## Verify Everything Works

### 1. Check UI Status
- Top of page should show: "✅ All services running"
- Metrics should show values (not "N/A")

### 2. Test Fault Injection
- Click "🧠 Inject Memory Leak"
- Should see "Memory leak injected!" message
- Heap usage should increase to 200+ MB

### 3. Test Agent
- Click "🚀 Launch Autonomous Agent"
- Should see spinner: "Agent working: Detect → Diagnose → Fix → Report..."
- After 30-60s, should see incident report

---

## Stopping the Application

### Stop Streamlit
Press `Ctrl+C` in the terminal running Streamlit

### Stop Docker Containers

**Option A - Use Batch Script**:
```bash
stop.bat
```

**Option B - Manual**:
```bash
docker compose down -v
```

---

## Uninstallation

### Remove Docker Containers
```bash
docker compose down -v
docker system prune -a --volumes
```

### Remove Python Packages
```bash
pip uninstall -y crewai langchain-groq streamlit prometheus-api-client requests fpdf docker flask prometheus_client
```

### Remove Docker Desktop
- Windows Settings → Apps → Docker Desktop → Uninstall

---

## Directory Structure

After installation, you should have:

```
ROBOCOP/
├── agents.py              # AI agent definitions
├── app.py                 # Streamlit UI
├── crew.py                # Agent orchestration
├── tools.py               # Agent tools
├── check-docker.py        # Health check script
├── docker-compose.yml     # Docker services config
├── prometheus.yml         # Prometheus config
├── loki-config.yml        # Loki config
├── requirements.txt        # Python dependencies
├── start.bat              # Windows startup script
├── stop.bat               # Windows stop script
├── test-services.bat      # Service test script
├── README.md              # Overview
├── QUICKSTART.md          # Quick start guide
├── INSTALL.md             # This file
├── TROUBLESHOOTING.md     # Problem solving
├── faulty-app/
│   ├── app.py             # Flask app with faults
│   ├── Dockerfile         # Container config
│   └── requirements.txt   # App dependencies
└── runbooks/
    ├── memory_leak.yml    # Memory leak playbook
    └── crash_loop.yml     # Crash loop playbook
```

---

## Next Steps

1. ✅ Installation complete
2. 📖 Read QUICKSTART.md for usage guide
3. 🔧 If issues, see TROUBLESHOOTING.md
4. 🚀 Start building your own agents!

---

## Useful Commands

```bash
# Start everything
start.bat

# Check health
python check-docker.py

# Test services
test-services.bat

# View logs
docker compose logs -f

# Restart a service
docker compose restart faulty-app

# Stop everything
stop.bat

# Launch UI
streamlit run app.py
```

---

## System Requirements Summary

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 64-bit |
| RAM | 4GB minimum, 8GB recommended |
| Disk | 2GB free space |
| Docker | Desktop 4.0+ |
| Python | 3.11 or higher |
| Internet | Required for API calls |

---

## Support

- **Quick Start**: See QUICKSTART.md
- **Troubleshooting**: See TROUBLESHOOTING.md
- **Docker Issues**: https://docs.docker.com/desktop/troubleshoot/overview/
- **Groq API**: https://console.groq.com/docs
