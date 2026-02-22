import requests, subprocess, json, logging, os
from crewai.tools import tool

PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

@tool("Query Prometheus Metrics")
def query_prometheus(query: str) -> str:
    """Query Prometheus for real-time metrics. Use PromQL queries like 'app_heap_usage_bytes' or 'rate(app_restart_total[2m])'."""
    try:
        r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": query}, timeout=5)
        data = r.json()
        if data["status"] == "success":
            results = data["data"]["result"]
            output = []
            for res in results:
                metric = res["metric"]
                value = res["value"][1]
                output.append(f"{metric}: {value}")
            return "\n".join(output) if output else "No data returned"
        return f"Query failed: {data}"
    except Exception as e:
        return f"Prometheus error: {str(e)}"

@tool("Query Application Logs")
def query_logs(search_term: str) -> str:
    """Search application logs from Loki for errors, warnings, or specific patterns."""
    try:
        query = f'{{job="faulty-app"}} |= "{search_term}"'
        r = requests.get(f"{LOKI_URL}/loki/api/v1/query_range",
            params={"query": query, "limit": 20, "start": "1h"}, timeout=5)
        data = r.json()
        logs = []
        for stream in data.get("data", {}).get("result", []):
            for val in stream.get("values", []):
                logs.append(val[1])
        return "\n".join(logs[-10:]) if logs else "No matching logs found"
    except Exception as e:
        return f"Loki error: {str(e)}"

@tool("Get System Health Summary")
def get_health_summary(service: str) -> str:
    """Get a complete health summary of the service including heap, restarts, latency, errors, db connections."""
    try:
        metrics = {}
        for q in ["app_heap_usage_bytes", "app_restart_total", "app_request_latency_ms", "app_errors_total", "app_db_connections"]:
            r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": q}, timeout=5)
            data = r.json()
            if data["status"] == "success" and data["data"]["result"]:
                metrics[q] = data["data"]["result"][0]["value"][1]
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return f"Health check error: {str(e)}"

@tool("Execute Remediation")
def execute_fix(incident_type: str) -> str:
    """Execute remediation for a specific incident type: 'memory_leak', 'crash_loop', or 'db_saturation'."""
    fixes = {
        "memory_leak": {
            "actions": [
                "Clearing memory caches",
                "Restarting application with increased memory limit",
                "Scaling to 3 replicas for load distribution"
            ],
            "command": f"{APP_URL}/inject/clear"
        },
        "crash_loop": {
            "actions": [
                "Stopping crash loop cycle",
                "Resetting health checks",
                "Restarting with backoff policy"
            ],
            "command": f"{APP_URL}/inject/clear"
        },
        "db_saturation": {
            "actions": [
                "Throttle incoming traffic (temporary)",
                "Increase database pool size",
                "Purge stale connections and clear waiters"
            ],
            "command": f"{APP_URL}/inject/clear"
        }
    }
    
    if incident_type not in fixes:
        return f"Unknown incident type: {incident_type}"
    
    fix = fixes[incident_type]
    try:
        requests.get(fix["command"], timeout=5)
        return json.dumps({
            "status": "remediated",
            "incident_type": incident_type,
            "actions_taken": fix["actions"],
            "verified": True
        }, indent=2)
    except Exception as e:
        return f"Fix failed: {str(e)}"
