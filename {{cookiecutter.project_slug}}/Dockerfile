FROM ghcr.io/ministryofjustice/analytical-platform-airflow-python-base:1.50.0@sha256:b7e2c0ea1e0758a7ba736797350817466a6c5dad15e0b0b7a3c1c3c2096fef13

ARG MOJAP_IMAGE_VERSION="default"
ENV MOJAP_IMAGE_VERSION=${MOJAP_IMAGE_VERSION}

WORKDIR /app

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment
RUN uv venv /app/.venv --python {{ cookiecutter.python_version }}

# Install dependencies
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache -r <(uv pip compile pyproject.toml)

# Copy application code
COPY src/ /app/src/

# Ensure non-root user can access app files
RUN chown -R analyticalplatform:analyticalplatform /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

# Switch to non-root user
USER analyticalplatform

# Expose port
EXPOSE 8000

{% if cookiecutter.project_type == 'api' %}
# FastAPI API
ENTRYPOINT ["python", "-m", "uvicorn", "{{ cookiecutter.project_slug }}.app:app", "--host", "0.0.0.0", "--port", "8000"]
{% elif cookiecutter.project_type == 'dashboard' %}
# Dashboard (blank for now)
ENTRYPOINT []
{% elif cookiecutter.project_type == 'batch' %}
ENTRYPOINT ["python", "-m", "{{ cookiecutter.project_slug }}.main"]
{% endif %}
