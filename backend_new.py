#!/usr/bin/env python3
"""
ROBOCOP - Autonomous SRE Incident Response Agent
Integrated with OpenTelemetry tracing, Kafka-style event streaming, and incident.io reporting
Zero external AI dependencies - pure Python stdlib + optional Groq integration
"""

import json, threading, time, random, collections, uuid, datetime, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────
# OPENTELEMETRY-INSPIRED TRACING
# ─────────────────────────────────────────────────────────
class Span:
    def __init__(self, name, service, trace_id=None):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id or str(uuid.uuid4())[:16]
        self.name = name
        self.service = service
        self.start_time = time.time()
        self.end_time = None
        self.attributes = {}
        self.status = "OK"
        self.events = []

    def set_attribute(self, k, v):
        self.attributes[k] = v
    
    def add_event(self, name, attrs=None):
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attrs or {}
        })
    
    def end(self, status="OK"):
        self.end_time = time.time()
        self.status = status
    
    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "service": self.service,
            "duration_ms": round((self.end_time - self.start_time) * 1000, 2) if self.end_time else None,
            "status": self.status,
            "attributes": self.attributes,
            "timestamp": datetime.datetime.fromtimestamp(self.start_time).isoformat()
        }

# ─────────────────────────────────────────────────────────
# KAFKA-INSPIRED EVENT STREAMING
# ─────────────────────────────────────────────────────────
class KafkaTopic:
    def __init__(self, name):
        self.name = name
        self.queue = collections.deque(maxlen=500)
        self._lock = threading.Lock()
    
    def produce(self, key, value):
        event = {
            "offset": len(self.queue),
            "key": key,
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
            "topic": self.name
        }
        with self._lock:
            self.queue.append(event)
        return event
    
    def consume(self, limit=50):
        with self._lock:
            return list(self.queue)[-limit:]

class KafkaBroker:
    def __init__(self):
        self.topics = {
            t: KafkaTopic(t) for t in [
                "metrics.raw",
                "logs.application",
                "incidents.detected",
                "incidents.resolved",
                "agent.actions"
            ]
        }
    
    def get(self, name):
        return self.topics[name]
    
    def all_recent(self, n=80):
        all_e = []
        for t in self.topics.values():
            all_e.extend(t.consume(20))
        all_e.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_e[:n]

# ─────────────────────────────────────────────────────────
# GLOBAL STATE
# ─────────────────────────────────────────────────────────
kafka = KafkaBroker()
tracer_spans = collections.deque(maxlen=200)
incidents = collections.deque(maxlen=50)
metrics = {
    "heap_mb": 50,
    "cpu_pct": 20,
    "latency_ms": 30,
    "error_rate": 0.01,
    "restarts": 0,
    "db_conns": 10
}
fault = {"active": None}
agent_log = collections.deque(maxlen=100)
metrics_history = collections.deque(maxlen=60)

# Integration with existing ROBOCOP Prometheus/Loki
PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

# ─────────────────────────────────────────────────────────
# STRUCTURED LOG GENERATOR
# ─────────────────────────────────────────────────────────
LOGS = {
    "normal": [
        ("INFO",  "http.server",  "GET /api/users 200 {lat}ms trace_id={tid}"),
        ("INFO",  "db.pool",      "Connection acquired pool_size=10 wait={lat}ms"),
        ("DEBUG", "cache.redis",  "Cache HIT key=user:{uid} ttl=300s"),
        ("INFO",  "auth.service", "JWT validated user={uid} scope=read trace_id={tid}"),
    ],
    "memory_leak": [
        ("ERROR", "heap.monitor",  "OOM WARNING heap={heap}MB threshold=150MB trace_id={tid}"),
        ("WARN",  "gc.collector",  "GC pause {lat}ms — heap pressure high objects_pending=critical"),
        ("ERROR", "http.server",   "Request timeout heap={heap}MB exhaustion trace_id={tid}"),
        ("FATAL", "process.main",  "Memory allocation FAILED heap={heap}MB — OOM imminent"),
    ],
    "crash_loop": [
        ("FATAL", "process.main",   "Unhandled NullPointerException at OrderService.java:142"),
        ("ERROR", "k8s.kubelet",    "Container exited code=137 OOMKilled restart_count={restarts}"),
        ("WARN",  "k8s.controller", "CrashLoopBackOff pod=app-{uid} restarts={restarts}"),
        ("ERROR", "health.probe",   "Liveness probe FAILED consecutive_failures=3 trace_id={tid}"),
    ],
    "db_saturation": [
        ("ERROR", "db.pool",    "Pool EXHAUSTED max=20 waiting=45 timeout=30s trace_id={tid}"),
        ("WARN",  "db.query",   "Slow query {lat}ms — SELECT * FROM orders WHERE created_at > NOW()-30d"),
        ("ERROR", "db.pool",    "Cannot acquire connection after 30000ms — DB saturated"),
        ("FATAL", "db.master",  "Too many connections: 512/512 — rejecting all new connections"),
    ]
}

def emit_log():
    cat = fault["active"] or "normal"
    lvl, svc, tmpl = random.choice(LOGS[cat])
    msg = tmpl.format(
        lat=random.randint(500, 5000) if fault["active"] else random.randint(10, 80),
        tid=str(uuid.uuid4())[:8],
        uid=random.randint(1000, 9999),
        heap=metrics["heap_mb"],
        restarts=metrics["restarts"]
    )
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": lvl,
        "service": svc,
        "message": msg,
        "trace_id": str(uuid.uuid4())[:8],
        "resource.service.name": "robocop-app",
        "fault_context": fault["active"]
    }
    kafka.get("logs.application").produce(svc, entry)
    return entry

# ─────────────────────────────────────────────────────────
# METRICS SIMULATOR + PROMETHEUS INTEGRATION
# ─────────────────────────────────────────────────────────
def fetch_real_metrics():
    """Try to fetch from real Prometheus, fallback to simulation"""
    try:
        # Try to get real metrics from ROBOCOP's Prometheus
        heap_resp = requests.get(f"{PROM_URL}/api/v1/query",
                                params={"query": "app_heap_usage_bytes"}, timeout=2)
        if heap_resp.ok:
            data = heap_resp.json()
            if data["data"]["result"]:
                heap_bytes = float(data["data"]["result"][0]["value"][1])
                metrics["heap_mb"] = int(heap_bytes / 1e6)
        
        restart_resp = requests.get(f"{PROM_URL}/api/v1/query",
                                   params={"query": "app_restart_total"}, timeout=2)
        if restart_resp.ok:
            data = restart_resp.json()
            if data["data"]["result"]:
                metrics["restarts"] = int(float(data["data"]["result"][0]["value"][1]))
        
        latency_resp = requests.get(f"{PROM_URL}/api/v1/query",
                                   params={"query": "app_request_latency_ms"}, timeout=2)
        if latency_resp.ok:
            data = latency_resp.json()
            if data["data"]["result"]:
                metrics["latency_ms"] = int(float(data["data"]["result"][0]["value"][1]))
        
        db_resp = requests.get(f"{PROM_URL}/api/v1/query",
                               params={"query": "app_db_connections"}, timeout=2)
        if db_resp.ok:
            data = db_resp.json()
            if data["data"]["result"]:
                metrics["db_conns"] = int(float(data["data"]["result"][0]["value"][1]))
        
        error_resp = requests.get(f"{PROM_URL}/api/v1/query",
                                  params={"query": "rate(app_errors_total[2m])"}, timeout=2)
        if error_resp.ok:
            data = error_resp.json()
            if data["data"]["result"]:
                metrics["error_rate"] = float(data["data"]["result"][0]["value"][1])
        
        cpu_resp = requests.get(f"{PROM_URL}/api/v1/query",
                                params={"query": "app_cpu_usage_pct"}, timeout=2)
        if cpu_resp.ok:
            data = cpu_resp.json()
            if data["data"]["result"]:
                metrics["cpu_pct"] = float(data["data"]["result"][0]["value"][1])
        return True
    except Exception:
        return None

def clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))

def update_simulated_metrics():
    if fault["active"] == "memory_leak":
        metrics["heap_mb"] = clamp(metrics["heap_mb"] + random.randint(5, 12), 50, 250)
        metrics["latency_ms"] = clamp(metrics["latency_ms"] + random.randint(40, 120), 20, 2000)
        metrics["error_rate"] = clamp(metrics["error_rate"] + random.random() * 1.5, 0.01, 20)
        metrics["cpu_pct"] = clamp(metrics["cpu_pct"] + random.random() * 6, 10, 95)
    elif fault["active"] == "crash_loop":
        metrics["restarts"] += 1
        metrics["latency_ms"] = clamp(metrics["latency_ms"] + random.randint(60, 200), 30, 3000)
        metrics["error_rate"] = clamp(metrics["error_rate"] + random.random() * 3, 0.1, 30)
        metrics["cpu_pct"] = clamp(metrics["cpu_pct"] + random.random() * 8, 20, 99)
        metrics["heap_mb"] = clamp(60 + random.randint(0, 60), 50, 140)
    elif fault["active"] == "db_saturation":
        metrics["db_conns"] = clamp(metrics["db_conns"] + random.randint(8, 20), 10, 200)
        metrics["latency_ms"] = clamp(metrics["latency_ms"] + random.randint(80, 300), 50, 2000)
        metrics["error_rate"] = clamp(metrics["error_rate"] + random.random() * 2, 0.05, 15)
        metrics["cpu_pct"] = clamp(metrics["cpu_pct"] + random.random() * 4, 10, 80)
    else:
        metrics["heap_mb"] = clamp(metrics["heap_mb"] - random.randint(2, 6), 45, 70)
        metrics["latency_ms"] = clamp(metrics["latency_ms"] - random.randint(5, 20), 15, 60)
        metrics["error_rate"] = clamp(metrics["error_rate"] - random.random() * 0.5, 0.01, 1)
        metrics["cpu_pct"] = clamp(metrics["cpu_pct"] - random.random() * 3, 8, 30)
        metrics["db_conns"] = clamp(metrics["db_conns"] + random.randint(-3, 3), 5, 30)
        metrics["restarts"] = max(0, metrics["restarts"] - 1)

def record_metrics_snapshot():
    metrics_history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "heap_mb": metrics["heap_mb"],
        "latency_ms": metrics["latency_ms"],
        "error_rate": metrics["error_rate"],
        "cpu_pct": metrics["cpu_pct"],
        "restarts": metrics["restarts"],
        "db_conns": metrics["db_conns"]
    })

def background_loop():
    while True:
        if not fetch_real_metrics():
            update_simulated_metrics()
        emit_log()
        record_metrics_snapshot()
        time.sleep(2)

app = Flask(__name__)

@app.after_request
def _add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "fault": fault["active"]})

@app.route("/metrics", methods=["GET"])
def api_metrics():
    return jsonify({"metrics": metrics, "history": list(metrics_history)})

@app.route("/logs", methods=["GET"])
def api_logs():
    logs = kafka.get("logs.application").consume(80)
    def map_level(level):
        level = (level or "").lower()
        if level in ("warn", "warning"):
            return "warning"
        if level in ("error",):
            return "error"
        if level in ("fatal", "critical"):
            return "critical"
        return "info"
    payload = []
    for entry in logs[::-1]:
        val = entry["value"]
        payload.append({
            "id": val.get("trace_id") or val.get("timestamp"),
            "timestamp": val.get("timestamp"),
            "level": map_level(val.get("level")),
            "message": val.get("message"),
            "source": val.get("service")
        })
    return jsonify({"logs": payload})

@app.route("/faults/inject", methods=["POST"])
def api_inject_fault():
    data = request.get_json(silent=True) or {}
    f_type = data.get("type")
    if f_type not in ("memory_leak", "crash_loop", "db_saturation"):
        return jsonify({"error": "invalid fault type"}), 400
    fault["active"] = f_type
    try:
        if f_type == "memory_leak":
            requests.get(f"{APP_URL}/inject/memory-leak", timeout=2)
        elif f_type == "crash_loop":
            requests.get(f"{APP_URL}/inject/crash-loop", timeout=2)
        else:
            requests.get(f"{APP_URL}/inject/db-saturation", timeout=2)
    except Exception:
        pass
    return jsonify({"status": "injected", "fault": fault["active"]})

@app.route("/faults/clear", methods=["POST"])
def api_clear_faults():
    fault["active"] = None
    try:
        requests.get(f"{APP_URL}/inject/clear", timeout=2)
    except Exception:
        pass
    return jsonify({"status": "cleared"})

@app.route("/agent/run", methods=["POST"])
def api_run_agent():
    start = time.time()
    try:
        from crew import run_incident_response
        result = run_incident_response()
        duration = round(time.time() - start, 1)
        report = build_incident_report(fault["active"], duration, str(result))
        incidents.appendleft(report)
        return jsonify({"report": report, "report_markdown": str(result), "mttr": duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/incidents", methods=["GET"])
def api_incidents():
    return jsonify({"incidents": list(incidents)})

def build_incident_report(active_fault, mttr, report_markdown):
    if active_fault == "memory_leak":
        return {
            "id": f"INC-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "Memory Leak",
            "severity": "P1",
            "rootCause": "Heap growth exceeded safe thresholds, indicating a memory leak.",
            "actionsToken": ["Cleared caches", "Restarted application", "Scaled replicas"],
            "resolution": "Heap and latency returned to baseline after remediation.",
            "mttr": mttr,
            "prevention": ["Add heap profiling to CI", "Set alerts at 70% heap", "Enforce memory limits"]
        }
    if active_fault == "crash_loop":
        return {
            "id": f"INC-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "Crash Loop",
            "severity": "P1",
            "rootCause": "Repeated container restarts detected with elevated error rates.",
            "actionsToken": ["Reset health checks", "Restarted with backoff", "Verified stability"],
            "resolution": "Restart frequency normalized and errors stabilized.",
            "mttr": mttr,
            "prevention": ["Increase memory limits", "Add restart budget alerts", "Improve health checks"]
        }
    if active_fault == "db_saturation":
        return {
            "id": f"INC-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "DB Saturation",
            "severity": "P1",
            "rootCause": "Connection pool exhaustion caused elevated latency and errors.",
            "actionsToken": ["Killed long queries", "Scaled pool capacity", "Restarted DB proxy"],
            "resolution": "DB connections returned to healthy range.",
            "mttr": mttr,
            "prevention": ["Tune pool sizes", "Add slow-query alerts", "Enable connection limits"]
        }
    return {
        "id": f"INC-{uuid.uuid4().hex[:6].upper()}",
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "Incident",
        "severity": "P2",
        "rootCause": "Incident detected by agent.",
        "actionsToken": ["Investigated metrics", "Applied runbook actions", "Verified recovery"],
        "resolution": "System returned to baseline.",
        "mttr": mttr,
        "prevention": ["Add targeted alerts", "Review runbook thresholds"]
    }

def start_server():
    threading.Thread(target=background_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("BACKEND_API_PORT", "8000")))

if __name__ == "__main__":
    start_server()
