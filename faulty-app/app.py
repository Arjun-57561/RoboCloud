from flask import Flask, jsonify
from prometheus_client import make_wsgi_app, Gauge, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import threading, time, logging, random

app = Flask(__name__)
heap_usage = Gauge('app_heap_usage_bytes', 'Simulated heap usage')
restart_counter = Counter('app_restart_total', 'Pod restart count')
error_counter = Counter('app_errors_total', 'Application errors')
request_latency = Gauge('app_request_latency_ms', 'Request latency')
db_connections = Gauge('app_db_connections', 'Simulated active DB connections')

leak_active = False
crash_active = False
db_sat_active = False
memory_store = []

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/inject/memory-leak')
def inject_leak():
    global leak_active
    leak_active = True
    logging.error("CRITICAL: Memory allocation surge detected in /app/server.py:142")
    return jsonify({"fault": "memory_leak", "status": "injected"})

@app.route('/inject/crash-loop')
def inject_crash():
    global crash_active
    crash_active = True
    logging.error("FATAL: Pod entering CrashLoopBackOff - exit code 137")
    return jsonify({"fault": "crash_loop", "status": "injected"})

@app.route('/inject/db-saturation')
def inject_db_saturation():
    global db_sat_active
    db_sat_active = True
    logging.error("DB Saturation: connection pool exhausted; waiting clients spiking")
    return jsonify({"fault": "db_saturation", "status": "injected"})

@app.route('/inject/clear')
def clear_faults():
    global leak_active, crash_active, db_sat_active, memory_store
    leak_active, crash_active, db_sat_active, memory_store = False, False, False, []
    heap_usage.set(50_000_000)
    db_connections.set(10)
    request_latency.set(30)
    return jsonify({"status": "cleared"})

def background_sim():
    # initialize base values
    db_connections.set(10)
    request_latency.set(30)
    while True:
        if leak_active:
            memory_store.append('x' * 10**5)
            heap_usage.set(min(50_000_000 + len(memory_store)*100_000, 250_000_000))
            logging.error(f"OOM Warning: heap={heap_usage._value.get()}")
        else:
            heap_usage.set(50_000_000 + random.randint(-5_000_000, 5_000_000))
        
        if crash_active:
            restart_counter.inc()
            error_counter.inc(random.randint(1,5))
            logging.error("Container restarted - CrashLoopBackOff")
        
        if db_sat_active:
            # ramp up DB connections, cap at 200 to simulate exhaustion
            cur = db_connections._value.get() or 10
            inc = random.randint(5, 20)
            db_connections.set(min(cur + inc, 200))
            # latency and errors typically increase under DB pressure
            request_latency.set(random.randint(600, 2000))
            error_counter.inc(random.randint(0, 3))
            if db_connections._value.get() >= 180:
                logging.error("DB Connection Saturation: pool at 90%+ utilization")
        else:
            # normal DB connection churn
            db_connections.set(max(5, min(30, int((db_connections._value.get() or 10) + random.randint(-3, 3)))))
            # latency normal unless memory leak active
            request_latency.set(random.randint(10, 50) if not leak_active else random.randint(200, 2000))
        time.sleep(2)

threading.Thread(target=background_sim, daemon=True).start()
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8080)
