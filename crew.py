from crewai import Crew, Task, Process
from agents import detector, diagnoser, actor, reporter
import datetime

def run_incident_response():
    timestamp = datetime.datetime.now().isoformat()
    
    detect_task = Task(
        description=f"[{timestamp}] Scan Prometheus metrics and Loki logs. Identify anomalies with exact values and thresholds crossed. Provide a short justification for why each is anomalous.",
        agent=detector,
        expected_output="Anomaly report with metric values, thresholds, and log excerpts with brief justifications"
    )
    
    diagnose_task = Task(
        description="Analyze anomalies to determine incident_type (memory_leak|crash_loop|db_saturation), probable root cause, severity (P1-P3), and blast radius. Explain your reasoning briefly.",
        agent=diagnoser,
        expected_output="Root cause analysis with incident_type, cause, severity, and concise reasoning",
        context=[detect_task]
    )
    
    fix_task = Task(
        description="Select the correct runbook and execute remediation. After actions, re-check metrics to verify recovery. Justify each action taken.",
        agent=actor,
        expected_output="Remediation actions executed with verification metrics and short justifications",
        context=[diagnose_task]
    )
    
    report_task = Task(
        description="Write a complete timestamped incident report covering detection, diagnosis, remediation (with actions and justifications), verification, and prevention recommendations.",
        agent=reporter,
        expected_output="Markdown incident report",
        context=[detect_task, diagnose_task, fix_task]
    )
    
    crew = Crew(
        agents=[detector, diagnoser, actor, reporter],
        tasks=[detect_task, diagnose_task, fix_task, report_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    safe_ts = timestamp.replace(':', '-')
    try:
        import os
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/incident-{safe_ts}.md', 'w', encoding='utf-8') as f:
            f.write(str(result))
    except Exception:
        pass
    return result

if __name__ == "__main__":
    print(run_incident_response())
