# FastAPI Template Guide

This guide explains how to use the included FastAPI example to quickly build and deploy REST APIs.

## What's Included

This template provides:

- **Minimal FastAPI app** (`src/template/app.py`) — production-ready example
- **Kubernetes health checks** — `/health` and `/ready` endpoints for pod probes
- **Structured logging** — environment-aware log configuration
- **Docker setup** — production Dockerfile with multi-stage build
- **Cloud Platform ready** — works with deployment manifests
- **Auto-generated API docs** — Swagger UI at `/docs`

## Quick Start

### 1. Run Locally

**Development mode (with auto-reload):**

```bash
uv run fastapi dev src/template/app.py
```

Then visit: http://localhost:8000

**Interactive API docs:** http://localhost:8000/docs

**Health checks:**
- http://localhost:8000/health
- http://localhost:8000/ready

### 3. Build Docker Image

The included `Dockerfile.api` uses the same Ministry of Justice approved base image as the main template:

```bash
docker build -f Dockerfile.api -t my-app:latest .
docker run -p 8000:8000 my-app:latest
```

### 4. Customise for Your API

Edit `src/template/app.py` to add your endpoints:

```python
@app.get("/api/v1/data")
async def get_data() -> JSONResponse:
    """Your data endpoint."""
    return JSONResponse({"data": [...]})

@app.post("/api/v1/process")
async def process_data(payload: dict) -> JSONResponse:
    """Process incoming data."""
    logger.info(f"Processing: {payload}")
    return JSONResponse({"status": "processed"})
```

## Kubernetes Deployment

The template includes ready-to-use Kubernetes manifests in `deployments/templates/`.

### Key Endpoints for Kubernetes

Your app provides:

| Endpoint | Purpose | Kubernetes Use |
|----------|---------|-----------------|
| `/health` | Liveness probe | Restart if fails |
| `/ready` | Readiness probe | Remove from load balancer if fails |
| `/docs` | Swagger UI | Manual testing & documentation |
| `/api/v1/*` | Your API | Client traffic |

### Configure Health Checks

Edit `deployments/templates/deployment.yml`:

```yaml
livenessProbe:
  httpGet:
    path: /health      # ← Your health endpoint
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready       # ← Your ready endpoint
    port: http
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 2
```

## Environment Configuration

The app reads these environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENVIRONMENT` | `development` | App environment (development/production) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `PORT` | `8000` | HTTP port to listen on |

Set in Kubernetes:

```yaml
# deployments/templates/deployment.yml
env:
  - name: ENVIRONMENT
    value: production
  - name: LOG_LEVEL
    value: INFO
```

## Testing

Add pytest tests for your endpoints:

```python
# tests/unit/test_app.py
from fastapi.testclient import TestClient
from src.template.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_hello():
    response = client.get("/api/v1/hello?name=Alice")
    assert response.status_code == 200
    assert "Alice" in response.json()["message"]
```

Run tests:

```bash
uv run pytest tests/
```

## Common Customisations

### Add CORS Support

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Add Request Logging Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response
```

### Add Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.get("/api/v1/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    return JSONResponse({"message": "Access granted"})
```
