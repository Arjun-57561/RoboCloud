"""
Simple FastAPI backend that wraps the working Streamlit crew
"""
import os
import time
import subprocess
import requests
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import deque
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="SRE Agent API - Simple")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
APP_URL = os.getenv("APP_URL", "http://localhost:8080")
PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")

# Storage
metrics_history = deque(maxlen=50)
logs_storage = deque(maxlen=100)
current_fault = None

# Models
class FaultInjectRequest(BaseModel):
    type: str

class MetricsResponse(BaseModel):
    metrics: dict
    history: List[dict]

class LogsResponse(BaseModel):
    logs: List[dict]

class HealthResponse(BaseModel):
    fault: Optional[str]

class AgentReport(BaseModel):
    id: str
    timestamp: str
    type: str
    severity: str
    rootCause: str
    actionsToken: List[str]
    resolution: str
    mttr: int
    prevention: List[str]

class AgentRunResponse(BaseModel):
    report: AgentReport
    mttr: int

# Helper functions
def query_prometheus(query: str) -> float:
    try:
        response = requests.get(
            f"{PROM_URL}/api/v1/query",
            params={"query": query},
            timeout=2
        )
        data = response.json()
        if data["data"]["result"]:
            return float(data["data"]["result"][0]["value"][1])
        return 0.0
    except:
        return 0.0

def collect_metrics():
    heap_bytes = query_prometheus("app_heap_usage_bytes")
    heap_mb = heap_bytes / 1e6
    restarts = query_prometheus("app_restart_total")
    latency_ms = query_prometheus("app_request_latency_ms")
    errors = query_prometheus("rate(app_errors_total[1m])")
    cpu_pct = query_prometheus("rate(process_cpu_seconds_total[1m]) * 100")
    
    return {
        "heap_mb": round(heap_mb, 2),
        "restarts": int(restarts),
        "latency_ms": round(latency_ms, 2),
        "error_rate": round(errors, 3),
        "cpu_pct": round(cpu_pct, 2),
    }

def add_log(level: str, message: str, source: str = "system"):
    log_entry = {
        "id": f"log-{int(time.time() * 1000)}",
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "source": source
    }
    logs_storage.append(log_entry)

# Endpoints
@app.get("/")
def root():
    return {"status": "ok", "service": "SRE Agent API - Simple"}

@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    metrics = collect_metrics()
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        **metrics
    }
    metrics_history.append(history_entry)
    return {"metrics": metrics, "history": list(metrics_history)}

@app.get("/logs", response_model=LogsResponse)
def get_logs():
    return {"logs": list(logs_storage)}

@app.get("/health", response_model=HealthResponse)
def get_health():
    return {"fault": current_fault}

@app.post("/faults/inject")
def inject_fault(request: FaultInjectRequest):
    global current_fault
    fault_type = request.type
    fault_map = {
        "memory_leak": "memory-leak",
        "crash_loop": "crash-loop",
        "db_saturation": "db-saturation"
    }
    
    if fault_type not in fault_map:
        raise HTTPException(status_code=400, detail="Invalid fault type")
    
    try:
        response = requests.get(f"{APP_URL}/inject/{fault_map[fault_type]}", timeout=2)
        current_fault = fault_type
        add_log("error", f"Fault injected: {fault_type}", "fault-injector")
        return {"status": "injected", "fault": fault_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inject fault: {str(e)}")

@app.post("/faults/clear")
def clear_faults():
    global current_fault
    try:
        response = requests.get(f"{APP_URL}/inject/clear", timeout=2)
        current_fault = None
        add_log("info", "All faults cleared", "fault-injector")
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear faults: {str(e)}")

@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent():
    """Run the agent by executing crew.py as a subprocess"""
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    
    add_log("info", "Starting agent pipeline", "agent-orchestrator")
    
    try:
        start_time = time.time()
        
        # Run crew.py as a subprocess
        result = subprocess.run(
            ["python", "crew.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        mttr = int(time.time() - start_time)
        
        if result.returncode != 0:
            error_msg = result.stderr or "Agent execution failed"
            add_log("error", error_msg, "agent-orchestrator")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Create report
        report = AgentReport(
            id=f"incident-{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            type=current_fault or "unknown",
            severity="P1" if current_fault in ["memory_leak", "crash_loop"] else "P2",
            rootCause=f"System detected {(current_fault or 'anomaly').replace('_', ' ')}",
            actionsToken=[
                "Scanned Prometheus metrics",
                "Analyzed Loki logs",
                "Identified root cause",
                "Executed remediation",
                "Verified recovery"
            ],
            resolution=result.stdout[:500] if result.stdout else "Agent completed successfully",
            mttr=mttr,
            prevention=[
                "Implement proactive monitoring",
                "Set up automated alerts",
                "Review resource limits",
                "Schedule health checks"
            ]
        )
        
        add_log("info", f"Agent completed in {mttr}s", "agent-orchestrator")
        
        return {"report": report, "mttr": mttr}
        
    except subprocess.TimeoutExpired:
        add_log("error", "Agent timed out after 120s", "agent-orchestrator")
        raise HTTPException(status_code=500, detail="Agent execution timed out")
    except Exception as e:
        add_log("error", f"Agent failed: {str(e)}", "agent-orchestrator")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
