# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

**Author:** {{ cookiecutter.author }}

## Project Type

This project is configured as a **{{ cookiecutter.project_type }}** workload.

### {{ cookiecutter.project_type | upper }}

## Getting Started

### 1. Setup Cloud Platform

See [`CLOUD_DEPLOYMENT.md`](./CLOUD_DEPLOYMENT.md) for complete setup:

1. Create Cloud Platform namespace in [`cloud-platform-environments`](https://github.com/ministryofjustice/cloud-platform-environments)
2. Configure GitHub repository secrets
3. Customise Kubernetes manifests in `deployments/`

### 2. Local Development

```bash
uv sync

{% if cookiecutter.project_type == 'api' %}
uv run fastapi dev src/{{ cookiecutter.project_slug }}/app.py
# Visit http://localhost:8000/docs for API docs
{% elif cookiecutter.project_type == 'dashboard' %}
uv run # for later
# Visit http://localhost:8501
{% elif cookiecutter.project_type == 'batch' %}
uv run python -m {{ cookiecutter.project_slug }}.main
{% endif %}
```

### 3. Build & Deploy

```bash
docker build -f Dockerfile -t {{ cookiecutter.project_slug }}:latest .

git push origin main

# See .github/workflows/
```
