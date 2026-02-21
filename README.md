# 🛡️ Autonomous Incident Response Agent

Production-grade SRE agent that detects, diagnoses, and remediates incidents automatically using CrewAI and Groq.

## Architecture

- **4 AI Agents**: Detector → Diagnoser → Actor → Reporter
- **Monitoring Stack**: Prometheus + Loki + Grafana
- **Faulty App**: Flask app with injectable faults
- **UI**: Streamlit dashboard

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Infrastructure

```bash
docker compose up -d
```

Wait 30 seconds for services to start.

### 3. Launch UI

```bash
streamlit run app.py
```

Open http://localhost:8501

### 4. Test the Agent

1. Click "Inject Memory Leak" → Metrics turn red
2. Click "Launch Autonomous Agent" → Watch 4 agents work
3. See incident report with MTTR (30-60s)

## Services

- **Streamlit UI**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Faulty App**: http://localhost:8080

## Agent Workflow

1. **Detector**: Scans Prometheus metrics + Loki logs for anomalies
2. **Diagnoser**: Determines root cause, severity, blast radius
3. **Actor**: Executes remediation from runbooks
4. **Reporter**: Generates post-mortem report

## Fault Types

- **Memory Leak**: Heap > 200MB, latency spikes
- **Crash Loop**: Restart count > 3/2min, exit code 137

## Runbooks

See `runbooks/` for YAML-based remediation playbooks.

## Configuration

1. Copy the example environment file:

```bash
copy .env.example .env
```

2. Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_actual_groq_api_key_here
```

The application will automatically load the API key from the `.env` file.

## Metrics

- `app_heap_usage_bytes`: Memory usage
- `app_restart_total`: Pod restarts
- `app_request_latency_ms`: Request latency
- `app_errors_total`: Error count

## Clean Up

```bash
docker compose down -v
```
