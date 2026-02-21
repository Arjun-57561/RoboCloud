# 🏗️ Architecture Documentation

## System Overview

The Autonomous Incident Response Agent is a multi-layered system that combines AI agents, monitoring infrastructure, and automated remediation.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    Streamlit Dashboard (app.py)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Service    │  │   Metrics    │  │  Fault Injection &   │  │
│  │    Health    │  │   Display    │  │  Agent Execution     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT LAYER                             │
│                   CrewAI Orchestration (crew.py)                │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Detector   │──▶│  Diagnoser   │──▶│    Actor     │──┐    │
│  │    Agent     │   │    Agent     │   │    Agent     │  │    │
│  └──────────────┘   └──────────────┘   └──────────────┘  │    │
│         │                   │                   │         │    │
│         │                   │                   │         ▼    │
│         │                   │                   │   ┌──────────┐│
│         │                   │                   │   │ Reporter ││
│         │                   │                   │   │  Agent   ││
│         │                   │                   │   └──────────┘│
│         └───────────────────┴───────────────────┘         │    │
│                              │                             │    │
│                    ┌─────────┴─────────┐                  │    │
│                    │   Tools Layer     │                  │    │
│                    │    (tools.py)     │                  │    │
│                    └───────────────────┘                  │    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│  Prometheus  │    │     Loki     │    │   Faulty App     │
│   :9090      │    │    :3100     │    │     :8080        │
│              │    │              │    │                  │
│  - Metrics   │    │  - Logs      │    │  - Flask API     │
│  - Alerts    │    │  - Search    │    │  - Metrics       │
│  - PromQL    │    │  - LogQL     │    │  - Faults        │
└──────────────┘    └──────────────┘    └──────────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │     Grafana      │
                    │      :3000       │
                    │  (Visualization) │
                    └──────────────────┘
```

---

## Component Details

### 1. User Interface Layer

**File**: `app.py`

**Responsibilities**:
- Display real-time metrics from Prometheus
- Show service health status
- Provide fault injection controls
- Trigger agent execution
- Display incident reports

**Key Features**:
- Service health checks with fallbacks
- Error handling for offline services
- Real-time metric updates
- Disabled buttons when services are down

**Technologies**: Streamlit, Requests

---

### 2. AI Agent Layer

#### Orchestration (`crew.py`)

**Responsibilities**:
- Coordinate agent execution
- Manage task dependencies
- Pass context between agents
- Return final results

**Workflow**:
```
detect_task → diagnose_task → fix_task → report_task
```

**Process**: Sequential (each agent waits for previous)

#### Agents (`agents.py`)

##### Detector Agent
- **Role**: Incident Detector
- **Goal**: Monitor metrics and detect anomalies
- **Tools**: query_prometheus, query_logs, get_health_summary
- **Triggers**:
  - Heap > 80% (200MB)
  - Restarts > 3 in 2 min
  - Latency > 500ms
  - Error rate spikes

##### Diagnoser Agent
- **Role**: Root Cause Analyst
- **Goal**: Determine exact root cause
- **Tools**: query_prometheus, query_logs
- **Outputs**:
  - Incident type (memory_leak, crash_loop)
  - Root cause
  - Severity (P1-P3)
  - Blast radius

##### Actor Agent
- **Role**: Remediation Engineer
- **Goal**: Execute fix and verify
- **Tools**: execute_fix, query_prometheus, get_health_summary
- **Actions**:
  - Select runbook
  - Execute remediation
  - Verify metrics return to normal

##### Reporter Agent
- **Role**: Incident Reporter
- **Goal**: Generate post-mortem
- **Tools**: None (uses context from other agents)
- **Outputs**:
  - Incident ID & timestamp
  - Detection details
  - Root cause analysis
  - Actions taken
  - Verification
  - Prevention recommendations

**LLM**: Groq (Llama 3.1 70B Versatile)

---

### 3. Tools Layer

**File**: `tools.py`

#### query_prometheus
- **Purpose**: Query Prometheus for metrics
- **Input**: PromQL query string
- **Output**: Metric values with labels
- **Example**: `app_heap_usage_bytes`

#### query_logs
- **Purpose**: Search Loki logs
- **Input**: Search term
- **Output**: Last 10 matching log entries
- **Example**: Search for "OOM" or "error"

#### get_health_summary
- **Purpose**: Get complete service health
- **Input**: Service name
- **Output**: JSON with all key metrics
- **Metrics**: heap, restarts, latency, errors

#### execute_fix
- **Purpose**: Execute remediation
- **Input**: Incident type (memory_leak, crash_loop)
- **Output**: Actions taken + verification
- **Actions**:
  - Clear memory caches
  - Restart application
  - Scale replicas
  - Reset health checks

---

### 4. Monitoring Layer

#### Prometheus (Port 9090)

**Purpose**: Time-series metrics database

**Configuration**: `prometheus.yml`
```yaml
scrape_interval: 5s
targets: ['faulty-app:8080']
```

**Metrics Collected**:
- `app_heap_usage_bytes` - Memory usage
- `app_restart_total` - Restart count
- `app_request_latency_ms` - Latency
- `app_errors_total` - Error count

**Query Language**: PromQL

#### Loki (Port 3100)

**Purpose**: Log aggregation system

**Configuration**: `loki-config.yml`
```yaml
storage: filesystem
schema: v11
retention: 24h
```

**Log Sources**: Faulty app container logs

**Query Language**: LogQL

#### Grafana (Port 3000)

**Purpose**: Visualization & dashboards

**Data Sources**:
- Prometheus (metrics)
- Loki (logs)

**Credentials**: admin/admin

---

### 5. Application Layer

#### Faulty App (Port 8080)

**File**: `faulty-app/app.py`

**Purpose**: Simulated application with injectable faults

**Endpoints**:
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /inject/memory-leak` - Inject memory leak
- `GET /inject/crash-loop` - Inject crash loop
- `GET /inject/clear` - Clear all faults

**Metrics Exposed**:
- `app_heap_usage_bytes` (Gauge)
- `app_restart_total` (Counter)
- `app_request_latency_ms` (Gauge)
- `app_errors_total` (Counter)

**Background Simulation**:
- Updates metrics every 2 seconds
- Simulates memory growth when leak active
- Simulates restarts when crash active
- Logs errors to stdout

**Technologies**: Flask, prometheus_client

---

## Data Flow

### Normal Monitoring Flow

```
1. Faulty App exposes metrics at /metrics
2. Prometheus scrapes metrics every 5s
3. Faulty App logs to stdout
4. Loki collects logs from container
5. Streamlit UI queries Prometheus for display
6. User sees real-time metrics
```

### Incident Response Flow

```
1. User clicks "Inject Memory Leak"
   └─▶ Faulty app starts allocating memory

2. Metrics spike (heap > 200MB)
   └─▶ Prometheus records high values

3. User clicks "Launch Agent"
   └─▶ Streamlit calls crew.kickoff()

4. Detector Agent runs
   ├─▶ Queries Prometheus: app_heap_usage_bytes
   ├─▶ Queries Loki: search for "OOM"
   └─▶ Detects anomaly: heap at 220MB

5. Diagnoser Agent runs
   ├─▶ Analyzes metrics + logs
   ├─▶ Identifies: memory_leak incident
   ├─▶ Determines: P1-critical severity
   └─▶ Outputs: Root cause analysis

6. Actor Agent runs
   ├─▶ Selects runbook: memory_leak.yml
   ├─▶ Executes: /inject/clear endpoint
   ├─▶ Verifies: Queries Prometheus again
   └─▶ Confirms: Heap back to 50MB

7. Reporter Agent runs
   ├─▶ Compiles all context
   ├─▶ Generates markdown report
   └─▶ Returns: Incident post-mortem

8. Streamlit displays report
   └─▶ User sees: MTTR 35s, incident resolved
```

---

## Deployment Architecture

### Docker Compose Services

```yaml
services:
  faulty-app:
    - Build: ./faulty-app/Dockerfile
    - Port: 8080
    - Memory: 256MB limit
    
  prometheus:
    - Image: prom/prometheus:latest
    - Port: 9090
    - Config: ./prometheus.yml
    
  loki:
    - Image: grafana/loki:2.9.0
    - Port: 3100
    - Config: ./loki-config.yml
    
  grafana:
    - Image: grafana/grafana:latest
    - Port: 3000
    - Depends: prometheus, loki
```

### Network

All services on same Docker network:
- Service discovery by name
- No external network access required
- Ports exposed to localhost only

---

## Security Architecture

### Current (Demo)
- ❌ No authentication on endpoints
- ❌ API key hardcoded in code
- ❌ Services exposed to localhost
- ❌ No TLS/SSL
- ❌ Default Grafana credentials

### Production Recommendations
- ✅ Add API authentication (JWT tokens)
- ✅ Use environment variables for secrets
- ✅ Implement RBAC for agent actions
- ✅ Add TLS for all services
- ✅ Use secrets management (Vault, AWS Secrets)
- ✅ Network policies for service isolation
- ✅ Audit logging for all agent actions

---

## Scalability Considerations

### Current Limitations
- Single instance of each service
- In-memory storage (Loki, Prometheus)
- No high availability
- Local Docker only

### Scaling Path
1. **Horizontal Scaling**:
   - Multiple faulty-app replicas
   - Prometheus federation
   - Loki clustering

2. **Storage**:
   - Persistent volumes for metrics
   - S3 for long-term log storage
   - Time-series database (Thanos)

3. **Agent Scaling**:
   - Parallel agent execution
   - Agent pool for multiple incidents
   - Queue-based task distribution

4. **Infrastructure**:
   - Kubernetes deployment
   - Cloud-native services
   - Auto-scaling based on load

---

## Performance Characteristics

### Latency
- Metric scrape: 5s interval
- Log ingestion: < 1s
- Agent detection: 5-10s
- Agent diagnosis: 10-20s
- Agent remediation: 5-10s
- Agent reporting: 10-20s
- **Total MTTR: 30-60s**

### Throughput
- Prometheus: 1000s metrics/sec
- Loki: 100s log lines/sec
- Agent: 1 incident at a time (sequential)

### Resource Usage
- Faulty App: 256MB RAM, 0.5 CPU
- Prometheus: 512MB RAM, 0.5 CPU
- Loki: 512MB RAM, 0.5 CPU
- Grafana: 256MB RAM, 0.25 CPU
- Streamlit: 256MB RAM, 0.25 CPU
- **Total: ~2GB RAM, 2 CPU cores**

---

## Technology Decisions

### Why CrewAI?
- Multi-agent orchestration
- Built-in task dependencies
- Context sharing between agents
- LangChain integration

### Why Groq?
- Fast inference (< 1s per agent)
- Free tier available
- Llama 3.1 70B quality
- Simple API

### Why Prometheus?
- Industry standard for metrics
- Powerful query language (PromQL)
- Pull-based model
- Service discovery

### Why Loki?
- Designed for logs (not full-text search)
- Efficient storage
- Grafana integration
- LogQL similar to PromQL

### Why Streamlit?
- Rapid UI development
- Python-native
- Real-time updates
- No frontend code needed

### Why Docker Compose?
- Simple local development
- Service orchestration
- Easy to understand
- Production-like environment

---

## Extension Points

### Adding New Agents
1. Define agent in `agents.py`
2. Add task in `crew.py`
3. Update workflow sequence

### Adding New Tools
1. Create tool function in `tools.py`
2. Decorate with `@tool`
3. Add to agent's tools list

### Adding New Faults
1. Add endpoint in `faulty-app/app.py`
2. Implement fault simulation
3. Create runbook in `runbooks/`
4. Update UI with injection button

### Adding New Metrics
1. Add metric in `faulty-app/app.py`
2. Update Prometheus scrape config
3. Add to UI display
4. Update agent detection logic

---

## Monitoring the Monitor

### Health Checks
- `check-docker.py` - Verify all services
- `test-services.bat` - Test endpoints
- Prometheus `/targets` - Scrape status
- Grafana dashboards - Visual monitoring

### Logs
- `docker compose logs -f` - All services
- `docker compose logs faulty-app` - Specific service
- Loki UI - Log search

### Metrics
- Prometheus UI - Query metrics
- Grafana - Visualize trends
- Streamlit - Real-time display

---

## Disaster Recovery

### Backup
- Prometheus data: Volume mount
- Loki data: Volume mount
- Configuration: Git repository

### Recovery
```bash
# Stop everything
docker compose down -v

# Restart fresh
docker compose up -d --build

# Verify
python check-docker.py
```

### Data Loss
- Metrics: Lost (in-memory)
- Logs: Lost (in-memory)
- Configuration: Preserved (Git)
- Agent code: Preserved (Git)

---

## Future Architecture

### Phase 1: Production Hardening
- Add authentication
- Implement secrets management
- Add TLS/SSL
- Persistent storage

### Phase 2: Kubernetes
- Deploy to K8s cluster
- Use real pod metrics
- Implement actual remediation
- Add more fault types

### Phase 3: Multi-Service
- Monitor multiple applications
- Cross-service incident detection
- Dependency mapping
- Blast radius calculation

### Phase 4: ML Enhancement
- Anomaly detection models
- Predictive incident detection
- Auto-tuning thresholds
- Pattern recognition

---

## Conclusion

This architecture provides a solid foundation for autonomous incident response with clear separation of concerns, extensibility, and production-ready patterns.

**Key Strengths**:
- Modular design
- Clear data flow
- Industry-standard tools
- Comprehensive monitoring
- Automated remediation

**Next Steps**: See QUICKSTART.md to get started!
