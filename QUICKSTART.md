# 🚀 Quick Start Guide - SRE Agent

## Prerequisites

1. **Docker Desktop** - Download from https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Wait for it to fully start (whale icon in system tray should be steady)

2. **Python 3.11+** - Check with: `python --version`

3. **Groq API Key** - Get free key from https://console.groq.com/

---

## Step 1: Install Python Dependencies (2 min)

```bash
pip install -r requirements.txt
```

---

## Step 2: Start Docker Containers (2 min)

```bash
# Start all services in background
docker compose up -d --build
```

Wait 30-60 seconds for services to initialize.

### Verify Docker is Running:

```bash
docker ps
```

You should see 4 containers running:
- `robocop-faulty-app-1`
- `robocop-prometheus-1`
- `robocop-loki-1`
- `robocop-grafana-1`

### Test Services Manually:

```bash
# Test faulty app
curl http://localhost:8080/health
# Should return: {"status": "healthy"}

# Test Prometheus
curl http://localhost:9090/-/ready
# Should return: Prometheus is Ready.
```

---

## Step 3: Launch Streamlit UI (1 min)

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Step 4: Test the Agent (2 min)

1. **Check Status**: Top of page should show "✅ All services running"
2. **Inject Fault**: Click "🧠 Inject Memory Leak"
3. **Watch Metrics**: Heap usage should spike to 200+ MB (red)
4. **Run Agent**: Click "🚀 Launch Autonomous Agent"
5. **See Results**: Agent detects → diagnoses → fixes → reports (30-60s)

---

## Troubleshooting

### Docker Not Found

**Error**: `docker: The term 'docker' is not recognized`

**Fix**: 
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Restart your terminal after installation
3. Verify: `docker --version`

### Port Already in Use

**Error**: `port is already allocated`

**Fix**:
```bash
docker compose down
docker compose up -d --build
```

### Containers Won't Start

**Fix**: Check logs to see what's failing:
```bash
docker compose up --build
# (without -d to see live logs)
```

Common issues:
- Docker Desktop not running → Start it and wait
- Insufficient memory → Give Docker 4GB+ in settings
- Files missing → Make sure all files from repo are present

### Streamlit Shows "Services Down"

**Fix**:
1. Check Docker: `docker ps` (should show 4 containers)
2. Wait 60 seconds after `docker compose up`
3. Test manually: `curl http://localhost:8080/health`
4. Restart containers: `docker compose restart`

### Agent Fails with API Error

**Fix**: Update Groq API key in `agents.py`:
```python
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key="YOUR_GROQ_KEY_HERE",  # Replace this
    temperature=0.1
)
```

Get free key: https://console.groq.com/

---

## Services & Ports

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit UI | http://localhost:8501 | Main dashboard |
| Faulty App | http://localhost:8080 | Flask app with metrics |
| Prometheus | http://localhost:9090 | Metrics database |
| Grafana | http://localhost:3000 | Visualization (admin/admin) |
| Loki | http://localhost:3100 | Log aggregation |

---

## Clean Up

Stop and remove all containers:
```bash
docker compose down -v
```

---

## Demo Flow

1. **Normal State**: All metrics green
2. **Inject Memory Leak**: Heap → 200+ MB, Latency → 500+ ms
3. **Launch Agent**:
   - Detector: Scans metrics, finds heap > 80%
   - Diagnoser: Identifies memory_leak incident
   - Actor: Executes remediation (clears cache, restarts)
   - Reporter: Generates post-mortem
4. **Verify Fix**: Metrics return to green
5. **MTTR**: 30-60 seconds end-to-end

---

## Next Steps

- View Grafana dashboards: http://localhost:3000 (admin/admin)
- Check Prometheus metrics: http://localhost:9090/graph
- Customize runbooks in `runbooks/` folder
- Add more fault types in `faulty-app/app.py`
- Tune agent prompts in `agents.py`

---

## Need Help?

1. Check Docker logs: `docker compose logs -f`
2. Check Streamlit logs in terminal
3. Verify all files exist: `ls -la`
4. Ensure Docker Desktop is running
5. Try clean restart: `docker compose down -v && docker compose up -d --build`
