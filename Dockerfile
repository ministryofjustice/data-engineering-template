FROM ghcr.io/ministryofjustice/analytical-platform-airflow-python-base:1.52.0@sha256:3eeb78a1d858e7452bbe4c4087adf5d0076d03c4c71b6bc3e33da9ed3eacaa44

ARG MOJAP_IMAGE_VERSION="default"
ENV MOJAP_IMAGE_VERSION=${MOJAP_IMAGE_VERSION}

# THIS IS AN EXAMPLE OF A DOCKERFILE FOR A PYTHON AIRFLOW IMAGE.
# IT IS NOT MEANT TO BE USED AS-IS

# Switch to root user to install packages
# USER root

# Copy requirements.txt
# COPY requirements.txt requirements.txt

# Copy application code
# COPY src/ .

# Install requirements
# RUN <<EOF
# pip install --no-cache-dir --requirement requirements.txt
# EOF

# Switch back to non-root user (analyticalplatform)
# USER ${CONTAINER_UID}

# Execute main.py script
# ENTRYPOINT ["python3", "main.py"]
