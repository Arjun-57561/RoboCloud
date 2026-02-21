from crewai import Crew, Task, Process
from agents import detector, diagnoser, actor, reporter
import datetime

def run_incident_response():
    timestamp = datetime.datetime.now().isoformat()
    
    detect_task = Task(
        description=f"[{timestamp}] Scan all metrics and logs. Report any anomalies with exact values.",
        agent=detector,
        expected_output="Anomaly report with metric values and log entries"
    )
    
    diagnose_task = Task(
        description="Analyze the detected anomalies. Determine incident type, root cause, severity, and blast radius.",
        agent=diagnoser,
        expected_output="Root cause analysis with incident_type, cause, severity",
        context=[detect_task]
    )
    
    fix_task = Task(
        description="Execute the appropriate remediation based on diagnosis. Verify fix by checking metrics after.",
        agent=actor,
        expected_output="Remediation result with verification",
        context=[diagnose_task]
    )
    
    report_task = Task(
        description="Write a complete incident report covering detection, diagnosis, remediation, and prevention.",
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
    return result

if __name__ == "__main__":
    print(run_incident_response())
