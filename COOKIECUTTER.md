# Data Engineering Template - Cookiecutter

This is a **Cookiecutter template** for bootstrapping new Python data engineering projects in the Ministry of Justice with **production-ready Kubernetes configurations**.

## Project Types

Choose one of two project types when creating your project:

### 1. **API** — REST APIs and backend services
- **Framework**: FastAPI (async, type-safe, auto-documented)
- **Kubernetes**: 3-replica deployment with pod anti-affinity for high availability
- **Ingress**: Tight security — `internal-non-prod` ingress class, rate-limited (10 RPS)
- **Network Policy**: Egress-only (DNS + HTTPS), no special ingress rules
- **Best for**: Data APIs, microservices, internal tools
- **Example**: Data ingestion API that receives events from external systems

### 2. **Dashboard** — Analytics dashboards and data visualization
- **Framework**: Streamlit (rapid UI development, great for dashboards)
- **Kubernetes**: 1-replica deployment (no scaling needed for read-only dashboards)
- **Ingress**: Less restrictive — `modsec` ingress class with oauth2-proxy authentication, ModSecurity WAF, HTTPS backend protocol
- **Network Policy**: Ingress from oauth2-proxy + prometheus (monitoring), restrictive egress (DNS + HTTPS)
- **Best for**: Analytical dashboards, BI tools, data exploration UIs
- **Example**: Electronic monitoring data visualization dashboard

### 3. **Data Pipelines** — Batch processing, ETFs, workflows
⚠️ **Not included in this template** — The MoJ Analytical Platform handles all batch orchestration and pipeline execution. Use the AP's dbt, Airflow, or other tools instead. No Kubernetes configuration needed.

---

## Quick Start

### 1. Create your project

```bash
uvx cookiecutter https://github.com/ministryofjustice/data-engineering-template
```

Answer the interactive prompts:
```
project_name [My Project]: hmpps-electronic-monitoring-data-dashboard
project_description: Display live EM cases on a dashboard
project_type (api/dashboard) [api]: dashboard
python_version (3.13/3.14) [3.14]: 3.14
```

### 2. Install and run

```bash
cd hmpps-electronic-monitoring-data-dashboard
uv sync

# For API projects
uv run fastapi dev src/hmpps_electronic_monitoring_data_dashboard/app.py

# For Dashboard projects
uv run streamlit run src/hmpps_electronic_monitoring_data_dashboard/app.py
```

Visit **http://localhost:8000** to see your project running.

---

## Kubernetes Deployment

Each generated project includes complete Kubernetes manifests tailored to its type. The post-generation hook automatically selects the correct files:

### API Deployments
- **Deployment**: `deployments/api/deployment.yml` (3 replicas, HA)
- **Ingress**: `deployments/templates/ingress.yml` (internal-non-prod, rate-limited 10 RPS)
- **Network Policy**: `deployments/templates/networkpolicy.yml` (egress-only: DNS + HTTPS)
- **Setup**: 3 replicas with pod anti-affinity, rolling updates, health checks at /health and /ready

### Dashboard Deployments
- **Deployment**: `deployments/dashboard/deployment.yml` (1 replica)
- **Ingress**: `deployments/templates/ingress.yml` (modsec class, oauth2-proxy protected)
- **Network Policy**: `deployments/templates/networkpolicy.yml` (ingress from oauth2-proxy + prometheus)
- **Setup**: 1 replica (no scaling), Recreate strategy, health checks at port 5000

### Shared Resources
All projects include:
- **Service** (`deployments/templates/service.yml`): ClusterIP service exposing your app
- **ServiceAccount** (`deployments/templates/serviceaccount.yml`): Pod identity for Cloud Platform integration

**Note**: The post-generation hook automatically selects type-specific ingress and networkpolicy files, then removes the unused ones. Generated projects only contain the files they need.

---

## Next Steps

### 1. Fill in placeholder values
Your generated project contains template variables like `{{environment}}`, `{{project_host}}`, `{{allowed_ips}}`. Replace these with actual values:
- Cloud Platform namespaces auto-populate these in CI/CD pipelines
- See `CLOUD_DEPLOYMENT.md` for integration details

### 2. Deploy to Cloud Platform
Each project scaffolds a `deployments/` directory ready for MoJ Cloud Platform:
```bash
# In your cloud-platform-environments PR
namespaces/live.cloud-platform.service.justice.gov.uk/hmpps-electronic-monitoring-data-dashboard/
```

### 3. View example implementations
- **API example**: See `src/template/app.py` (production FastAPI with logging, config, health endpoints)
- **Dashboard example**: See generated dashboard stub (Streamlit starter template)

---

## Modifying Your Project

### Switch frameworks
- API → Use FastAPI, Flask, or Django by editing `Dockerfile` ENTRYPOINT
- Dashboard → Use Streamlit, Plotly Dash, or Gradio by editing dependencies and `Dockerfile`

### Add dependencies
```bash
uv add pandas sqlalchemy psycopg2
uv sync
```

### Customize Kubernetes
All K8s YAML files support Jinja2 conditionals (`{% if cookiecutter.project_type == 'api' %}`). Edit as needed:
- Increase replicas: Edit `spec.replicas` in `deployments/api/deployment.yml`
- Change resource limits: Edit `resources.requests` and `resources.limits`
- Add volume mounts: Edit `spec.template.spec.containers[0].volumeMounts`

---

## Security & Best Practices

- **Images**: Uses MoJ-approved base image (scanned, signed) from ghcr.io/ministryofjustice/
- **Non-root user**: All containers run as `analyticalplatform` user
- **Network policies**: Type-specific egress/ingress rules enforce zero-trust networking
- **oauth2-proxy**: Dashboard projects enforce authentication at ingress level
- **ModSecurity**: Dashboard ingress includes Web Application Firewall (WAF) protection
- **Scanning**: Images scanned for CVEs; apply patches via base image updates

---

## Troubleshooting

### Application won't start?
Check logs in generated project:
```bash
# Local development
uv run pytest tests/

# Docker
docker build -t my-project:latest .
docker run -it my-project:latest
```

### Kubernetes deployment stuck?
```bash
# Check pod events
kubectl describe pod -n <namespace> <pod-name>

# Check logs
kubectl logs -n <namespace> <pod-name>

# Check ingress
kubectl describe ingress -n <namespace>
```

### Need to modify ingress rules?
Edit `deployments/templates/ingress.yml` — file structure is self-documenting with separate blocks for API vs Dashboard.

---

## Questions?

- **Cloud Platform setup**: See `CLOUD_DEPLOYMENT.md`
- **FastAPI development**: See `FASTAPI_TEMPLATE.md`
- **Python project structure**: See generated `README.md`
