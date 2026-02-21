import streamlit as st
import requests, json, time

from crew import run_incident_response

st.set_page_config(page_title="🛡️ SRE Agent", layout="wide")
st.title("🛡️ Autonomous Incident Response Agent")

# Check Docker services status
def check_service(url, name):
    try:
        r = requests.get(url, timeout=2)
        return True
    except:
        return False

services_status = {
    "faulty-app": check_service("http://localhost:8080/health", "faulty-app"),
    "prometheus": check_service("http://localhost:9090/-/ready", "prometheus"),
    "loki": check_service("http://localhost:3100/ready", "loki")
}

all_services_up = all(services_status.values())

# Status banner
if not all_services_up:
    st.error("⚠️ Docker containers not running! Start them with: `docker compose up -d --build`")
    with st.expander("🔧 Service Status Details"):
        for service, status in services_status.items():
            st.write(f"{'✅' if status else '❌'} {service}: {'Running' if status else 'Down'}")
        st.code("""
# Start Docker containers:
docker compose up -d --build

# Check status:
docker ps

# View logs:
docker compose logs -f
        """)
else:
    st.success("✅ All services running")

st.divider()

col1, col2, col3 = st.columns(3)

# Metrics display with error handling
try:
    health = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_heap_usage_bytes"}, timeout=2).json()
    heap = float(health["data"]["result"][0]["value"][1]) if health["data"]["result"] else 0
    col1.metric("Heap Usage", f"{heap/1e6:.0f} MB", delta=f"{'🔴 CRITICAL' if heap > 200e6 else '🟢 Normal'}")
except:
    col1.metric("Heap Usage", "N/A", help="Prometheus not available")

try:
    restarts = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_restart_total"}, timeout=2).json()
    r_val = float(restarts["data"]["result"][0]["value"][1]) if restarts["data"]["result"] else 0
    col2.metric("Restarts", f"{r_val:.0f}", delta=f"{'🔴 HIGH' if r_val > 5 else '🟢 Normal'}")
except:
    col2.metric("Restarts", "N/A", help="Prometheus not available")

try:
    latency = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_request_latency_ms"}, timeout=2).json()
    l_val = float(latency["data"]["result"][0]["value"][1]) if latency["data"]["result"] else 0
    col3.metric("Latency", f"{l_val:.0f} ms", delta=f"{'🔴 SLOW' if l_val > 500 else '🟢 Normal'}")
except:
    col3.metric("Latency", "N/A", help="Prometheus not available")

st.divider()

# Fault injection with error handling
st.subheader("💉 Fault Injection")
c1, c2, c3 = st.columns(3)

if c1.button("🧠 Inject Memory Leak", use_container_width=True, disabled=not services_status["faulty-app"]):
    try:
        requests.get("http://localhost:8080/inject/memory-leak", timeout=2)
        st.error("Memory leak injected!")
    except:
        st.warning("⚠️ faulty-app not running. Start Docker first.")

if c2.button("💀 Inject Crash Loop", use_container_width=True, disabled=not services_status["faulty-app"]):
    try:
        requests.get("http://localhost:8080/inject/crash-loop", timeout=2)
        st.error("Crash loop injected!")
    except:
        st.warning("⚠️ faulty-app not running. Start Docker first.")

if c3.button("🧹 Clear All Faults", use_container_width=True, disabled=not services_status["faulty-app"]):
    try:
        requests.get("http://localhost:8080/inject/clear", timeout=2)
        st.success("Faults cleared!")
    except:
        st.warning("⚠️ faulty-app not running. Start Docker first.")

st.divider()

# Agent run
st.subheader("🤖 Run Agent")
if st.button("🚀 Launch Autonomous Agent", type="primary", use_container_width=True, disabled=not all_services_up):
    with st.spinner("Agent working: Detect → Diagnose → Fix → Report..."):
        try:
            start = time.time()
            result = run_incident_response()
            elapsed = time.time() - start
            st.success(f"✅ Incident resolved in {elapsed:.1f}s (MTTR)")
            st.markdown("### 📋 Incident Report")
            st.markdown(str(result))
        except Exception as e:
            st.error(f"❌ Agent execution failed: {str(e)}")
            st.info("Make sure all Docker services are running and Groq API key is valid.")

if not all_services_up:
    st.info("💡 Agent is disabled until all services are running. Start Docker containers first.")
