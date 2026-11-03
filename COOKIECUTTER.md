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

Each generated project includes **single, shared** Kubernetes manifests that use Jinja2 conditionals to adapt to the project type:

### Files Generated

- **`deployments/api/deployment.yml` or `deployments/dashboard/deployment.yml`**
  - Type-specific Deployment configuration
  - API: 3 replicas, RollingUpdate strategy, HA pod anti-affinity
  - Dashboard: 1 replica, Recreate strategy

- **`deployments/templates/ingress.yml`** (conditional content)
  - API section: `internal-non-prod` class, rate-limited (10 RPS), direct backend
  - Dashboard section: `modsec` class, oauth2-proxy protection, ModSecurity WAF

- **`deployments/templates/networkpolicy.yml`** (conditional content)
  - API section: Egress-only (DNS + HTTPS)
  - Dashboard section: Ingress from oauth2-proxy + prometheus, restricted egress

- **`deployments/templates/service.yml`, `serviceaccount.yml`** (shared)
  - Used by both API and dashboard projects

### Template Variables

Generated projects use placeholder variables in `${UPPERCASE}` format that must be filled in by users during Cloud Platform setup:

- **`${ENVIRONMENT}`** → Kubernetes namespace suffix (dev/staging/prod)
- **`${PROJECT_HOST}`** → DNS hostname for ingress
- **`${IMAGE_TAG}`** → Docker image version/tag
- **`${ECR_REGISTRY}`** → AWS ECR registry URL
- **`${ALLOWED_IPS}`** → IP ranges (dashboard only, for modsecurity whitelist)
- **`${GITHUB_TEAM}`** → Your GitHub team (dashboard only, for audit logs)

These are NOT filled by cookiecutter—they're meant for manual configuration by Cloud Platform operators.

---

## Next Steps After Generation

### 1. Fill in Cloud Platform Variables

The generated project contains placeholder variables (in `${VAR}` format) that must be replaced during Cloud Platform namespace setup:

**In `deployments/templates/ingress.yml`:**
- `${ENVIRONMENT}` → dev/staging/prod
- `${PROJECT_HOST}` → your.domain.cloud-platform.service.justice.gov.uk

**In all deployment files:**
- `${ENVIRONMENT}` → dev/staging/prod
- `${IMAGE_TAG}` → Image version (e.g., v1.0.0, latest)
- `${ECR_REGISTRY}` → AWS ECR registry URL (e.g., 123456789.dkr.ecr.eu-west-1.amazonaws.com)

**For Dashboard projects in `deployments/templates/ingress.yml`:**
- `${ALLOWED_IPS}` → IP ranges for whitelist (e.g., 10.0.0.0/8, 203.0.113.0/24)
- `${GITHUB_TEAM}` → Your GitHub team name for audit logs

### 2. Deploy to Cloud Platform

```bash
# 1. Create namespace in cloud-platform-environments
cd ~/cloud-platform-environments
mkdir -p namespaces/live.cloud-platform.service.justice.gov.uk/my-project-dev
cp -r /path/to/generated/deployments/templates/* namespaces/.../

# 2. Replace all ${VAR} placeholders in your YAML files
sed -i 's/${ENVIRONMENT}/dev/g' namespaces/.../deployments/**/*.yml
sed -i 's/${IMAGE_TAG}/v1.0.0/g' namespaces/.../deployments/**/*.yml
# ... etc for all variables

# 3. Submit PR to cloud-platform-environments
git add namespaces/
git commit -m "Add my-project namespace with K8s manifests"
git push origin -u feature/my-project
```

### 3. Configure CI/CD

Update your repository's GitHub Actions to:
1. Build and push Docker image to ECR with proper tag
2. Update deployment manifests with actual `${IMAGE_TAG}`
3. Deploy using kubectl or GitOps tool

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
