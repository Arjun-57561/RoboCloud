# 🚀 START HERE - SRE Agent Setup

Welcome! This is your production-grade Autonomous Incident Response Agent.

## ⚡ Quick Setup (5 minutes)

### 1️⃣ Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop/
- Install and start it (wait for whale icon to be steady)

### 2️⃣ Get Groq API Key (Free)
- Visit: https://console.groq.com/
- Sign up and create API key
- Copy the key (starts with `gsk_`)

### 3️⃣ Configure API Key
Edit `agents.py` line 7:
```python
api_key="gsk_YOUR_KEY_HERE",  # Paste your key here
```

### 4️⃣ Run Setup Script
Double-click: `start.bat`

This will:
- ✅ Check Docker is installed
- ✅ Start all containers (Prometheus, Loki, Grafana, Faulty App)
- ✅ Wait for services to initialize
- ✅ Verify everything is healthy

### 5️⃣ Launch UI
```bash
streamlit run app.py
```

Open http://localhost:8501

---

## 🎯 Test It Works

1. **Check Status**: Top should show "✅ All services running"
2. **Inject Fault**: Click "🧠 Inject Memory Leak"
3. **Run Agent**: Click "🚀 Launch Autonomous Agent"
4. **See Magic**: Agent detects → diagnoses → fixes → reports (30-60s)

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | You are here! |
| **QUICKSTART.md** | Detailed step-by-step guide |
| **INSTALL.md** | Full installation instructions |
| **TROUBLESHOOTING.md** | Fix common issues |
| **README.md** | Project overview |

---

## 🛠️ Useful Scripts

| Script | What It Does |
|--------|--------------|
| `start.bat` | Start all Docker services |
| `stop.bat` | Stop all Docker services |
| `test-services.bat` | Test if services are running |
| `check-docker.py` | Python health check |

---

## ❌ Having Issues?

### Docker not found?
→ Install Docker Desktop first

### Services not starting?
```bash
docker compose logs -f
```
Look for error messages

### Streamlit shows "Services Down"?
```bash
python check-docker.py
```
Wait 60 seconds after starting Docker

### Agent fails?
→ Check Groq API key in `agents.py`

**Full troubleshooting**: See TROUBLESHOOTING.md

---

## 🏗️ What You Built

- **4 AI Agents**: Detector, Diagnoser, Actor, Reporter
- **Monitoring Stack**: Prometheus + Loki + Grafana
- **Faulty App**: Flask app with injectable faults
- **Autonomous Remediation**: 30-60s MTTR

---

## 🎓 How It Works

1. **Detector Agent**: Scans Prometheus metrics + Loki logs
2. **Diagnoser Agent**: Identifies root cause (memory leak, crash loop, etc.)
3. **Actor Agent**: Executes fix from runbooks
4. **Reporter Agent**: Generates incident post-mortem

All fully autonomous!

---

## 🔗 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Streamlit UI | http://localhost:8501 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Faulty App | http://localhost:8080 | - |
| Loki | http://localhost:3100 | - |

---

## 🧪 Demo Scenarios

### Scenario 1: Memory Leak
1. Click "Inject Memory Leak"
2. Watch heap spike to 200+ MB
3. Launch agent
4. Agent clears cache and restarts app
5. Heap returns to normal

### Scenario 2: Crash Loop
1. Click "Inject Crash Loop"
2. Watch restart count increase
3. Launch agent
4. Agent stops crash cycle
5. Pod stabilizes

---

## 🎨 Customize It

- **Add Faults**: Edit `faulty-app/app.py`
- **Add Runbooks**: Create YAML in `runbooks/`
- **Tune Agents**: Edit prompts in `agents.py`
- **Add Tools**: Create new tools in `tools.py`

---

## 🧹 Clean Up

Stop everything:
```bash
stop.bat
```

Remove all containers:
```bash
docker compose down -v
```

---

## 🚀 Next Steps

1. ✅ Get it running (you're almost there!)
2. 📖 Read QUICKSTART.md for detailed usage
3. 🎯 Try both fault scenarios
4. 🔧 Customize for your use case
5. 🏆 Build your own agents!

---

## 💡 Pro Tips

- **First time?** Docker will download images (~500MB), be patient
- **Slow startup?** Give Docker 4GB+ RAM in settings
- **Agent too slow?** Try `llama-3.1-8b-instant` model
- **Want more faults?** Add them in `faulty-app/app.py`

---

## ✅ Checklist

Before running, ensure:
- [ ] Docker Desktop installed and running
- [ ] Groq API key configured in `agents.py`
- [ ] Python 3.11+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Containers started: `start.bat` or `docker compose up -d --build`
- [ ] Services healthy: `python check-docker.py`

---

## 🎉 Ready to Go!

You now have a production-grade autonomous incident response system!

**Start with**: `streamlit run app.py`

**Questions?** Check TROUBLESHOOTING.md

**Let's go! 🚀**
