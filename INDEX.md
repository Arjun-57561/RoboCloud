# 📑 Documentation Index

Complete guide to the Autonomous Incident Response Agent project.

---

## 🚀 Getting Started (Read in Order)

1. **[START_HERE.md](START_HERE.md)** ⭐
   - Quick 5-minute setup guide
   - What you need to get started
   - First-time user walkthrough
   - **Start here if you're new!**

2. **[QUICKSTART.md](QUICKSTART.md)**
   - Detailed step-by-step instructions
   - Testing and verification
   - Demo flow walkthrough
   - Troubleshooting basics

3. **[INSTALL.md](INSTALL.md)**
   - Complete installation guide
   - Prerequisites and dependencies
   - System requirements
   - Uninstallation instructions

---

## 📚 Reference Documentation

4. **[README.md](README.md)**
   - Project overview
   - Quick reference
   - Key features
   - Technology stack

5. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - System architecture diagrams
   - Component details
   - Data flow
   - Technology decisions
   - Scalability considerations

6. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
   - Complete project details
   - Files created
   - Performance metrics
   - Success criteria
   - Future enhancements

---

## 🔧 Troubleshooting & Support

7. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
   - Common issues and solutions
   - Diagnostic commands
   - Error messages explained
   - Quick reference table

---

## 📂 File Organization

### Core Application Files
```
agents.py              - 4 AI agents (Detector, Diagnoser, Actor, Reporter)
app.py                 - Streamlit UI with error handling
crew.py                - Agent orchestration and workflow
tools.py               - 4 CrewAI tools for monitoring and remediation
```

### Configuration Files
```
docker-compose.yml     - Docker services orchestration
prometheus.yml         - Prometheus scrape configuration
loki-config.yml        - Loki storage configuration
requirements.txt       - Python dependencies
.dockerignore          - Docker build optimization
.gitignore             - Git exclusions
```

### Faulty Application
```
faulty-app/
  ├── app.py           - Flask app with metrics and fault injection
  ├── Dockerfile       - Container definition
  └── requirements.txt - App-specific dependencies
```

### Runbooks
```
runbooks/
  ├── memory_leak.yml  - Memory leak remediation playbook
  └── crash_loop.yml   - Crash loop remediation playbook
```

### Automation Scripts
```
start.bat              - Windows startup automation
stop.bat               - Windows shutdown automation
test-services.bat      - Service health testing
check-docker.py        - Python health checker
```

### Documentation (7 files)
```
START_HERE.md          - Quick start guide ⭐
QUICKSTART.md          - Detailed walkthrough
INSTALL.md             - Installation instructions
TROUBLESHOOTING.md     - Problem solving
README.md              - Project overview
ARCHITECTURE.md        - Technical architecture
PROJECT_SUMMARY.md     - Complete project details
INDEX.md               - This file
```

---

## 🎯 Quick Navigation

### I want to...

**Get started quickly**
→ [START_HERE.md](START_HERE.md)

**Follow detailed steps**
→ [QUICKSTART.md](QUICKSTART.md)

**Install from scratch**
→ [INSTALL.md](INSTALL.md)

**Fix an issue**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**See what was built**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**Get a quick overview**
→ [README.md](README.md)

---

## 📖 Reading Paths

### Path 1: Quick Start (15 minutes)
1. START_HERE.md - Setup
2. Run `start.bat`
3. Run `streamlit run app.py`
4. Test the agent

### Path 2: Comprehensive (45 minutes)
1. START_HERE.md - Overview
2. INSTALL.md - Full installation
3. QUICKSTART.md - Detailed walkthrough
4. ARCHITECTURE.md - Understanding the system
5. Test all scenarios

### Path 3: Troubleshooting
1. TROUBLESHOOTING.md - Find your issue
2. Check diagnostic commands
3. Review logs
4. Fix and verify

### Path 4: Deep Dive (2 hours)
1. README.md - Overview
2. ARCHITECTURE.md - System design
3. PROJECT_SUMMARY.md - Complete details
4. Read source code
5. Customize and extend

---

## 🔍 Search by Topic

### Docker
- Installation: INSTALL.md → Prerequisites
- Starting: START_HERE.md → Step 4
- Troubleshooting: TROUBLESHOOTING.md → Docker Issues
- Architecture: ARCHITECTURE.md → Deployment

### Agents
- Overview: README.md → Architecture
- Details: ARCHITECTURE.md → AI Agent Layer
- Configuration: agents.py (source code)
- Workflow: ARCHITECTURE.md → Data Flow

### Monitoring
- Setup: QUICKSTART.md → Step 3
- Metrics: README.md → Metrics Tracked
- Architecture: ARCHITECTURE.md → Monitoring Layer
- Troubleshooting: TROUBLESHOOTING.md → Metrics Show N/A

### UI
- Launch: START_HERE.md → Step 5
- Features: README.md → Demo Flow
- Troubleshooting: TROUBLESHOOTING.md → Streamlit Issues
- Architecture: ARCHITECTURE.md → User Interface Layer

### API Keys
- Getting: START_HERE.md → Step 2
- Configuration: INSTALL.md → Step 2
- Troubleshooting: TROUBLESHOOTING.md → Agent Fails

---

## 📊 Documentation Statistics

- **Total Documentation**: 7 markdown files
- **Total Words**: ~15,000 words
- **Total Files in Project**: 31 files
- **Lines of Code**: ~1,500 lines
- **Docker Services**: 4 containers
- **AI Agents**: 4 agents
- **Tools**: 4 tools
- **Runbooks**: 2 playbooks

---

## 🎓 Learning Resources

### Beginner
- START_HERE.md - Get running quickly
- QUICKSTART.md - Learn by doing
- README.md - Understand what it does

### Intermediate
- ARCHITECTURE.md - System design
- Source code - Implementation details
- Runbooks - Remediation patterns

### Advanced
- PROJECT_SUMMARY.md - Complete overview
- Extend agents - Add new capabilities
- Custom runbooks - New incident types

---

## 🛠️ Maintenance

### Regular Tasks
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Clean Docker: `docker system prune -a`
- Check health: `python check-docker.py`
- View logs: `docker compose logs -f`

### Documentation Updates
- Keep API keys current in examples
- Update version numbers
- Add new troubleshooting entries
- Document new features

---

## 🤝 Contributing

### Adding Documentation
1. Follow existing format
2. Use clear headings
3. Include code examples
4. Add to this index

### Improving Docs
- Fix typos and errors
- Add missing information
- Clarify confusing sections
- Add more examples

---

## 📞 Support

### Self-Service
1. Check TROUBLESHOOTING.md
2. Review relevant documentation
3. Check logs: `docker compose logs -f`
4. Run health check: `python check-docker.py`

### Common Questions

**Q: Where do I start?**
A: START_HERE.md

**Q: Docker won't start?**
A: TROUBLESHOOTING.md → Docker Issues

**Q: How does it work?**
A: ARCHITECTURE.md

**Q: Agent fails?**
A: TROUBLESHOOTING.md → Agent Errors

**Q: Want to customize?**
A: ARCHITECTURE.md → Extension Points

---

## ✅ Documentation Checklist

Before running the system:
- [ ] Read START_HERE.md
- [ ] Check prerequisites in INSTALL.md
- [ ] Have Docker Desktop installed
- [ ] Have Groq API key ready
- [ ] Understand basic workflow from README.md

After first run:
- [ ] Verify all services with check-docker.py
- [ ] Test fault injection
- [ ] Run agent end-to-end
- [ ] Review ARCHITECTURE.md for deeper understanding

For troubleshooting:
- [ ] Check TROUBLESHOOTING.md first
- [ ] Run diagnostic commands
- [ ] Review service logs
- [ ] Verify configuration

---

## 🎉 You're Ready!

All documentation is complete and organized. Start with [START_HERE.md](START_HERE.md) and you'll be running in 5 minutes!

**Quick Start**: `start.bat` → `streamlit run app.py` → Test agent

**Questions?** Check the relevant doc from the list above.

**Let's go! 🚀**
