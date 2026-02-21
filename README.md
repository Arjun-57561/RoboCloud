# 🛡️ Autonomous Incident Response Agent

Production-grade SRE agent that detects, diagnoses, and remediates incidents automatically using CrewAI and Groq.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Python 3.11+
- Groq API Key (free): https://console.groq.com/

### Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Groq API key in agents.py (line 7)
# api_key="gsk_YOUR_KEY_HERE"

# 3. Start Docker services
start.bat
# OR: docker compose up -d --build

# 4. Launch UI
streamlit run app.py
```

Open http://localhost:8501 and test the agent!

**📖 New here? Start with [START_HERE.md](START_HERE.md)**

---

## 🎯 What It Does

1. **Detects** incidents by monitoring Prometheus metrics + Loki logs
2. **Diagnoses** root cause (memory leak, crash loop, etc.)
3. **Fixes** the issue automatically using runbooks
4. **Reports** incident post-mortem with MTTR

**Mean Time To Resolution: 30-60 seconds** ⚡

---

## 🏗️ Architecture

- **4 AI Agents**: Detector → Diagnoser → Actor → Reporter
- **Monitoring Stack**: Prometheus + Loki + Grafana
- **Faulty App**: Flask app with injectable faults
- **UI**: Streamlit dashboard

```
Streamlit UI → CrewAI Agents → Tools → Prometheus/Loki/Faulty-App
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | **👈 Start here!** Quick overview |
| [QUICKSTART.md](QUICKSTART.md) | Detailed step-by-step guide |
| [INSTALL.md](INSTALL.md) | Full installation instructions |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix common issues |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Complete project details |

---

## 🎬 Demo Flow

1. **Normal State**: All metrics green ✅
2. **Inject Fault**: Click "🧠 Inject Memory Leak"
3. **Watch Metrics**: Heap → 200+ MB 🔴
4. **Run Agent**: Click "🚀 Launch Autonomous Agent"
5. **See Magic**: 
   - Detector finds anomaly
   - Diagnoser identifies memory leak
   - Actor executes fix
   - Reporter generates post-mortem
6. **Verify**: Metrics return to green ✅
7. **MTTR**: 30-60 seconds ⚡

---

## 🛠️ Useful Commands

```bash
# Start everything
start.bat

# Check health
python check-docker.py

# Test services
test-services.bat

# View logs
docker compose logs -f

# Stop everything
stop.bat

# Launch UI
streamlit run app.py
```

---

## 🔧 Services

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit UI | http://localhost:8501 | Main dashboard |
| Prometheus | http://localhost:9090 | Metrics database |
| Grafana | http://localhost:3000 | Visualization (admin/admin) |
| Faulty App | http://localhost:8080 | Flask app with metrics |
| Loki | http://localhost:3100 | Log aggregation |

---

## 🎭 Fault Scenarios

### Memory Leak
- Heap usage > 200MB (80% of limit)
- Latency spikes > 500ms
- Agent clears cache and restarts

### Crash Loop
- Restart count > 3 in 2 minutes
- Exit code 137 (OOM killed)
- Agent stops cycle and resets health checks

---

## 📊 Metrics Tracked

- `app_heap_usage_bytes` - Memory consumption
- `app_restart_total` - Pod restart count
- `app_request_latency_ms` - Request latency
- `app_errors_total` - Application errors

---

## 🔍 Agent Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
│ Detector │ --> │Diagnoser │ --> │  Actor   │ --> │Reporter│
└──────────┘     └──────────┘     └──────────┘     └────────┘
     │                 │                 │               │
  Monitors         Analyzes         Executes        Generates
  metrics/logs     root cause       runbook         post-mortem
```

---

## 🎓 Technology Stack

- **AI**: CrewAI + Groq (Llama 3.1 70B)
- **Monitoring**: Prometheus + Loki + Grafana
- **App**: Flask + Streamlit
- **Infra**: Docker Compose
- **Language**: Python 3.11+

---

## 🚨 Troubleshooting

### Docker not found?
Install Docker Desktop and restart terminal

### Services not starting?
```bash
docker compose logs -f
```

### Streamlit shows "Services Down"?
```bash
python check-docker.py
```
Wait 60 seconds after starting Docker

### Agent fails?
Check Groq API key in `agents.py`

**Full guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📦 Project Structure

```
ROBOCOP/
├── agents.py              # 4 AI agents
├── app.py                 # Streamlit UI
├── crew.py                # Agent orchestration
├── tools.py               # Agent tools
├── docker-compose.yml     # Services config
├── start.bat              # Windows startup
├── stop.bat               # Windows shutdown
├── check-docker.py        # Health checker
├── faulty-app/            # Flask app with faults
├── runbooks/              # Remediation playbooks
└── docs/                  # Documentation
```

---

## 🎯 Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Groq API key configured in `agents.py`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Containers started: `start.bat`
- [ ] Services healthy: `python check-docker.py`
- [ ] UI accessible: http://localhost:8501
- [ ] Fault injection works
- [ ] Agent completes full cycle

---

## 🔮 Future Enhancements

- More fault types (DB, network, CPU)
- Slack/email notifications
- Historical incident dashboard
- Multi-service monitoring
- Predictive incident detection
- Real Kubernetes integration

---

## 📝 Configuration

Update Groq API key in `agents.py`:

```python
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key="gsk_YOUR_KEY_HERE",  # Get from https://console.groq.com/
    temperature=0.1
)
```

---

## 🧹 Clean Up

```bash
# Stop containers
stop.bat

# Remove everything
docker compose down -v
```

---

## 🎉 Ready to Go!

**Start here**: [START_HERE.md](START_HERE.md)

**Quick start**: `start.bat` → `streamlit run app.py` → Inject fault → Run agent

**Questions?** Check the docs or TROUBLESHOOTING.md

**Let's build autonomous systems! 🚀**
