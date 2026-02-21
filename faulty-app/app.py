from flask import Flask, jsonify
from prometheus_client import make_wsgi_app, Gauge, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import threading, time, logging, random

app = Flask(__name__)
heap_usage = Gauge('app_heap_usage_bytes', 'Simulated heap usage')
restart_counter = Counter('app_restart_total', 'Pod restart count')
error_counter = Counter('app_errors_total', 'Application errors')
request_latency = Gauge('app_request_latency_ms', 'Request latency')

leak_active = False
crash_active = False
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

@app.route('/inject/clear')
def clear_faults():
    global leak_active, crash_active, memory_store
    leak_active, crash_active, memory_store = False, False, []
    heap_usage.set(50_000_000)
    return jsonify({"status": "cleared"})

def background_sim():
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
        
        request_latency.set(random.randint(10, 50) if not leak_active else random.randint(200, 2000))
        time.sleep(2)

threading.Thread(target=background_sim, daemon=True).start()
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8080)
