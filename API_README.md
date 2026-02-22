# FastAPI Backend for SRE Agent Dashboard

This is the REST API backend that powers the Next.js frontend dashboard.

## Quick Start

```bash
# Start the API server
python api.py
# OR
start-api.bat
```

The API will be available at: http://localhost:8000

## API Endpoints

### GET /
Health check endpoint
- Returns: `{"status": "ok", "service": "SRE Agent API"}`

### GET /metrics
Get current system metrics and historical data
- Returns: Current metrics (heap, restarts, latency, errors, CPU) and history

### GET /logs
Get recent system logs
- Returns: Array of log entries with timestamp, level, message, source

### GET /health
Get system health status and active fault
- Returns: `{"fault": "memory_leak" | "crash_loop" | "db_saturation" | null}`

### POST /faults/inject
Inject a fault into the system
- Body: `{"type": "memory_leak" | "crash_loop" | "db_saturation"}`
- Returns: `{"status": "injected", "fault": "..."}`

### POST /faults/clear
Clear all active faults
- Returns: `{"status": "cleared"}`

### POST /agent/run
Run the autonomous agent pipeline
- Returns: Incident report with MTTR and resolution details

## Environment Variables

Configure in `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
APP_URL=http://localhost:8080
PROMETHEUS_URL=http://localhost:9090
LOKI_URL=http://localhost:3100
```

## Architecture

```
Next.js Frontend (port 3001)
    ↓
FastAPI Backend (port 8000)
    ↓
Docker Services:
  - Faulty App (port 8080)
  - Prometheus (port 9090)
  - Loki (port 3100)
  - Grafana (port 3000)
```

## Running Everything

1. Start Docker services:
   ```bash
   docker compose up -d --build
   ```

2. Start FastAPI backend:
   ```bash
   python api.py
   ```

3. Start Streamlit UI (optional):
   ```bash
   streamlit run app.py
   ```

4. Start Next.js frontend:
   ```bash
   cd ../frontend
   npm run dev
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CORS Configuration

The API allows requests from:
- http://localhost:3000
- http://localhost:3001

To add more origins, edit the `allow_origins` list in `api.py`.
