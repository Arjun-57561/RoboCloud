import os
from dotenv import load_dotenv
from crewai import Agent
from langchain_groq import ChatGroq
from tools import query_prometheus, query_logs, get_health_summary, execute_fix

# Load environment variables
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to backend/.env and restart Streamlit.")

llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=groq_key,
    temperature=0.1
)

detector = Agent(
    role="Incident Detector",
    goal="Monitor cloud system metrics and detect anomalies in real-time",
    backstory="""You are a senior SRE monitoring specialist. You analyze Prometheus metrics 
    and Loki logs to detect incidents. You flag anomalies when:
    - Heap usage > 80% (200MB+ of 256MB limit)
    - Restart count increasing (>3 in 2 min)
    - Latency > 500ms
    - Error rate spikes""",
    tools=[query_prometheus, query_logs, get_health_summary],
    llm=llm,
    verbose=True
)

diagnoser = Agent(
    role="Root Cause Analyst",
    goal="Determine the exact root cause of detected incidents",
    backstory="""You are an expert incident analyst. Given metrics and logs, you determine:
    1. Incident type (memory_leak, crash_loop, db_saturation)
    2. Root cause (specific code path, resource exhaustion, config error)
    3. Severity (P1-critical, P2-high, P3-medium)
    4. Blast radius (which services affected)""",
    tools=[query_prometheus, query_logs],
    llm=llm,
    verbose=True
)

actor = Agent(
    role="Remediation Engineer",
    goal="Execute the correct fix based on diagnosis and verify recovery",
    backstory="""You are an automated remediation bot. You:
    1. Select the right runbook based on incident type
    2. Execute the fix
    3. Verify metrics return to normal after fix
    Always confirm fix worked by re-checking metrics.""",
    tools=[execute_fix, query_prometheus, get_health_summary],
    llm=llm,
    verbose=True
)

reporter = Agent(
    role="Incident Reporter",
    goal="Generate a detailed, human-readable incident report",
    backstory="""You write professional incident post-mortems. Include:
    - Incident ID and timestamp
    - What was detected (metrics/logs)
    - Root cause analysis
    - Actions taken and timeline
    - Verification that fix worked
    - Prevention recommendations
    Format as a clean markdown report.""",
    llm=llm,
    verbose=True
)
