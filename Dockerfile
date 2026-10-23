FROM ghcr.io/ministryofjustice/analytical-platform-airflow-python-base:1.55.0@sha256:76e462d63b5303a1203c2299140d2ac1f39aedffe922e918a99671c558c75418

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
