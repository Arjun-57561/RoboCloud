import streamlit as st
import requests, json, time
from crew import run_incident_response

st.set_page_config(page_title="🛡️ SRE Agent", layout="wide")
st.title("🛡️ Autonomous Incident Response Agent")

col1, col2, col3 = st.columns(3)

# Metrics display
try:
    health = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_heap_usage_bytes"}).json()
    heap = float(health["data"]["result"][0]["value"][1]) if health["data"]["result"] else 0
    col1.metric("Heap Usage", f"{heap/1e6:.0f} MB", delta=f"{'🔴 CRITICAL' if heap > 200e6 else '🟢 Normal'}")
except:
    col1.metric("Heap Usage", "N/A")

try:
    restarts = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_restart_total"}).json()
    r_val = float(restarts["data"]["result"][0]["value"][1]) if restarts["data"]["result"] else 0
    col2.metric("Restarts", f"{r_val:.0f}", delta=f"{'🔴 HIGH' if r_val > 5 else '🟢 Normal'}")
except:
    col2.metric("Restarts", "N/A")

try:
    latency = requests.get("http://localhost:9090/api/v1/query",
        params={"query": "app_request_latency_ms"}).json()
    l_val = float(latency["data"]["result"][0]["value"][1]) if latency["data"]["result"] else 0
    col3.metric("Latency", f"{l_val:.0f} ms", delta=f"{'🔴 SLOW' if l_val > 500 else '🟢 Normal'}")
except:
    col3.metric("Latency", "N/A")

st.divider()

# Fault injection
st.subheader("💉 Fault Injection")
c1, c2, c3 = st.columns(3)
if c1.button("🧠 Inject Memory Leak", use_container_width=True):
    requests.get("http://localhost:8080/inject/memory-leak")
    st.error("Memory leak injected!")
if c2.button("💀 Inject Crash Loop", use_container_width=True):
    requests.get("http://localhost:8080/inject/crash-loop")
    st.error("Crash loop injected!")
if c3.button("🧹 Clear All Faults", use_container_width=True):
    requests.get("http://localhost:8080/inject/clear")
    st.success("Faults cleared!")

st.divider()

# Agent run
st.subheader("🤖 Run Agent")
if st.button("🚀 Launch Autonomous Agent", type="primary", use_container_width=True):
    with st.spinner("Agent working: Detect → Diagnose → Fix → Report..."):
        start = time.time()
        result = run_incident_response()
        elapsed = time.time() - start
    st.success(f"✅ Incident resolved in {elapsed:.1f}s (MTTR)")
    st.markdown("### 📋 Incident Report")
    st.markdown(str(result))
