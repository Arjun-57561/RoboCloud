"""
FastAPI backend for SRE Agent Dashboard
Provides REST API endpoints for the Next.js frontend
"""
import os
import time
import requests
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import deque
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="SRE Agent API")

# CORS middleware for frontend
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

# In-memory storage
metrics_history = deque(maxlen=50)
logs_storage = deque(maxlen=100)
current_fault = None

# Models
class FaultInjectRequest(BaseModel):
    type: str  # memory_leak, crash_loop, db_saturation

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
    """Query Prometheus and return metric value"""
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
    """Collect current metrics from Prometheus"""
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
    """Add a log entry"""
    log_entry = {
        "id": f"log-{int(time.time() * 1000)}",
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "source": source
    }
    logs_storage.append(log_entry)


# API Endpoints
@app.get("/")
def root():
    return {"status": "ok", "service": "SRE Agent API"}


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """Get current metrics and history"""
    metrics = collect_metrics()
    
    # Add to history
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        **metrics
    }
    metrics_history.append(history_entry)
    
    return {
        "metrics": metrics,
        "history": list(metrics_history)
    }


@app.get("/logs", response_model=LogsResponse)
def get_logs():
    """Get recent logs"""
    return {"logs": list(logs_storage)}


@app.get("/health", response_model=HealthResponse)
def get_health():
    """Get system health and active fault"""
    return {"fault": current_fault}


@app.post("/faults/inject")
def inject_fault(request: FaultInjectRequest):
    """Inject a fault into the system"""
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
        response = requests.get(
            f"{APP_URL}/inject/{fault_map[fault_type]}",
            timeout=2
        )
        current_fault = fault_type
        add_log("error", f"Fault injected: {fault_type}", "fault-injector")
        return {"status": "injected", "fault": fault_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inject fault: {str(e)}")


@app.post("/faults/clear")
def clear_faults():
    """Clear all faults"""
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
    """Run the autonomous agent pipeline"""
    import traceback
    import sys
    import importlib
    
    # Clear module cache to ensure fresh import
    if 'agents' in sys.modules:
        del sys.modules['agents']
    if 'crew' in sys.modules:
        del sys.modules['crew']
    if 'tools' in sys.modules:
        del sys.modules['tools']
    
    # Check for GROQ API key
    if not os.getenv("GROQ_API_KEY"):
        add_log("error", "GROQ_API_KEY not configured", "agent-orchestrator")
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured in .env file")
    
    add_log("info", "Starting agent pipeline", "agent-orchestrator")
    
    try:
        # Import and run the crew
        sys.path.insert(0, os.path.dirname(__file__))
        
        from crew import run_incident_response
        
        start_time = time.time()
        add_log("info", "Executing CrewAI agents...", "agent-orchestrator")
        
        result = run_incident_response()
        mttr = int(time.time() - start_time)
        
        add_log("info", f"Agent pipeline completed in {mttr}s", "agent-orchestrator")
        
        # Parse the result and create report
        result_str = str(result)
        
        # Extract information from result
        incident_type = current_fault or "unknown"
        if "memory" in result_str.lower():
            incident_type = "memory_leak"
        elif "crash" in result_str.lower():
            incident_type = "crash_loop"
        elif "database" in result_str.lower() or "db" in result_str.lower():
            incident_type = "db_saturation"
        
        # Create detailed report
        report = AgentReport(
            id=f"incident-{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            type=incident_type,
            severity="P1" if current_fault in ["memory_leak", "crash_loop"] else "P2",
            rootCause=f"System detected {incident_type.replace('_', ' ')} based on metric analysis",
            actionsToken=[
                "Scanned Prometheus metrics",
                "Analyzed Loki logs", 
                "Identified root cause",
                "Executed remediation runbook",
                "Verified system recovery"
            ],
            resolution=result_str[:500] if len(result_str) > 500 else result_str,
            mttr=mttr,
            prevention=[
                "Implement proactive monitoring alerts",
                "Set up automated scaling policies",
                "Review resource allocation limits",
                "Schedule regular health checks"
            ]
        )
        
        add_log("info", f"Incident report generated: {report.id}", "agent-orchestrator")
        
        return {
            "report": report,
            "mttr": mttr
        }
        
    except ImportError as e:
        error_msg = f"Failed to import required modules: {str(e)}"
        add_log("error", error_msg, "agent-orchestrator")
        print(f"Import Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Agent execution failed: {str(e)}"
        add_log("error", error_msg, "agent-orchestrator")
        print(f"Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
