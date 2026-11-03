# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

**Author:** {{ cookiecutter.author }}

## Project Type

This project is configured as a **{{ cookiecutter.project_type }}** workload.

### {{ cookiecutter.project_type | upper }}

{% if cookiecutter.project_type == 'api' %}
**REST API Backend with FastAPI**
- High-availability setup with multiple replicas
- Load balanced across availability zones
- Automatic health checks and self-healing
- Auto-scaling based on load
- TLS/HTTPS via cert-manager

**Kubernetes setup:**
- Deployment with 3 replicas
- Service for load balancing
- Ingress for TLS routing
- NetworkPolicy for traffic control
- ServiceAccount for Kubernetes API access

**Terraform (cloud-platform-environments):**
- ECR repository for image storage
- Auto-scaling group configuration
- ALB for load balancing
- RDS for database (optional)
{% elif cookiecutter.project_type == 'dashboard' %}
**Dashboard/Frontend with Streamlit/Plotly**
- Single replica (scales manually)
- Lightweight resource usage
- Simple HTTP routing
- TLS/HTTPS via cert-manager

**Kubernetes setup:**
- Single-replica Deployment
- Service for internal routing
- Ingress for external access
- NetworkPolicy for basic security
- ServiceAccount for pod identity

**Terraform (cloud-platform-environments):**
- ECR repository for image storage
- Ingress routing configuration
- Pod security policies
{% elif cookiecutter.project_type == 'batch' %}
**Batch Data Processing Job**
- Scheduled execution via Kubernetes CronJob
- No replicas (runs once per schedule)
- No ingress (internal only)
- Long-running workloads supported
- Persistent volumes for state (if needed)

**Kubernetes setup:**
- CronJob for scheduling
- Job template for execution
- ServiceAccount for permissions
- NetworkPolicy for egress only (to data sources)

**Terraform (cloud-platform-environments):**
- ECR repository for image storage
- PVC for persistent storage (if needed)
- IAM roles for AWS access
- Secrets for credentials
{% endif %}

## Getting Started

### 1. Setup Cloud Platform

See [`CLOUD_DEPLOYMENT.md`](./CLOUD_DEPLOYMENT.md) for complete setup:

1. Create Cloud Platform namespace in [`cloud-platform-environments`](https://github.com/ministryofjustice/cloud-platform-environments)
2. Configure GitHub repository secrets
3. Customize Kubernetes manifests in `deployments/`

### 2. Local Development

```bash
# Install dependencies
uv sync

# Run locally
{% if cookiecutter.project_type == 'api' %}
uv run fastapi dev src/{{ cookiecutter.project_slug }}/app.py
# Visit http://localhost:8000/docs for API docs
{% elif cookiecutter.project_type == 'dashboard' %}
uv run streamlit run src/{{ cookiecutter.project_slug }}/app.py
# Visit http://localhost:8501
{% elif cookiecutter.project_type == 'batch' %}
uv run python -m {{ cookiecutter.project_slug }}.main
{% endif %}
```

### 3. Build & Deploy

```bash
# Build Docker image
docker build -f Dockerfile -t {{ cookiecutter.project_slug }}:latest .

# Push to ECR (from GitHub Actions)
git push origin main

# Deploy to Kubernetes (from GitHub Actions)
# See .github/workflows/
```

## Directory Structure

```
{{ cookiecutter.project_slug }}/
├── src/
│   └── {{ cookiecutter.project_slug }}/
│       └── app.py              # Your application code
├── tests/
│   └── unit/
│       └── test_app.py
├── deployments/
│   ├── templates/              # Shared K8s resources
│   │   ├── service.yml
│   │   ├── ingress.yml
│   │   ├── serviceaccount.yml
│   │   └── networkpolicy.yml
│   ├── {{ cookiecutter.project_type }}/        # Type-specific resources
│   │   {% if cookiecutter.project_type == 'api' %}└── deployment.yml    # 3 replicas, HA
│   {% elif cookiecutter.project_type == 'dashboard' %}└── deployment.yml    # 1 replica
│   {% elif cookiecutter.project_type == 'batch' %}└── cronjob.yml      # Scheduled job
│   {% endif %}└── ...
├── .github/workflows/          # CI/CD
├── Dockerfile
├── pyproject.toml
├── CLOUD_DEPLOYMENT.md         # Setup guide
└── README.md
```

## Kubernetes Manifests

Type-specific manifests are in `deployments/{{ cookiecutter.project_type }}/`:

- **deployment.yml** (API/Dashboard) — Kubernetes Deployment spec
- **cronjob.yml** (Batch) — Kubernetes CronJob spec

Shared templates in `deployments/templates/`:

- **service.yml** — Exposes to network
- **ingress.yml** — External routing
- **networkpolicy.yml** — Traffic control
- **serviceaccount.yml** — Pod identity

Customize all manifests with your configuration!

## Environment Variables

Configure in `deployments/templates/deployment.yml`:

- `ENVIRONMENT` — development/staging/production
- `LOG_LEVEL` — DEBUG/INFO/WARNING/ERROR

## Testing

```bash
uv run pytest tests/
```

## Deployment

See [`CLOUD_DEPLOYMENT.md`](./CLOUD_DEPLOYMENT.md) for:
- Cloud Platform namespace setup
- GitHub Actions configuration
- Kubernetes deployment steps
- Troubleshooting

## Service Catalogue

Register your project in MoJ's Service Catalogue:

See [`SERVICE_CATALOGUE.md`](./SERVICE_CATALOGUE.md) for:
- Registration options
- Metadata to provide
- Governance integration

## Support

- Cloud Platform issues: `#ask-cloud-platform`
- Data engineering: `#data-engineering`
- This template: GitHub issues

---

**Python {{ cookiecutter.python_version }}** | **Project Type: {{ cookiecutter.project_type }}**
