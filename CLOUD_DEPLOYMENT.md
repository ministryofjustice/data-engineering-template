# Cloud Deployment Guide

This guide explains how to set up cloud deployment (AWS ECR + Kubernetes) for projects built from this template.

## Overview

The template includes a CI/CD pipeline that:

1. **Builds a Docker image** on every PR and push to main
2. **Pushes to AWS ECR** with your specified registry
3. **Automatically deploys to development** on PR and main branch push
4. **Supports manual deployment** to development, preproduction, or production environments

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Repository                                      │
│                                                         │
│  Pull Request / Push to main                           │
│         ↓                                                │
│    docker-publish.yml                                   │
│    (orchestrator workflow)                              │
│         ↓                                                │
│    docker-build-push-template.yml                       │
│    (reusable build/push logic)                          │
│         ↓                                                │
│    AWS ECR                                              │
│    (Docker image registry)                              │
│         ↓                                                │
│    (Optional) deploy-to-environment.yml                 │
│    (manual Kubernetes deployment)                       │
│         ↓                                                │
│    EKS / Kubernetes Cluster                            │
│    (runs your application)                              │
└─────────────────────────────────────────────────────────┘
```

---

## Setup Steps

### 1. Create Cloud Platform Namespace (MoJ)

**This is the first step!** Infrastructure is managed via the Ministry of Justice Cloud Platform.

#### 1a. Create Namespace Configuration

1. Fork/clone the [cloud-platform-environments](https://github.com/ministryofjustice/cloud-platform-environments) repository
2. Create a new namespace folder:
   ```
   namespaces/live.cloud-platform.service.justice.gov.uk/your-project-name-dev/
   ```
3. Copy the structure from an existing data project (e.g., `hmpps-electronic-monitoring-data-validation-dev`)
4. Update the Terraform files:
   - `resources/ecr.tf` - Configure ECR repository and GitHub OIDC
   - `resources/variables.tf` - Set your project details
   - `00-namespace.yaml` - Create Kubernetes namespace
   - Other resource files as needed

#### 1b. Configure ECR with GitHub OIDC

In `resources/ecr.tf`:

```hcl
module "ecr" {
  source = "github.com/ministryofjustice/cloud-platform-terraform-ecr-credentials?ref=8.0.0"

  repo_name = var.namespace

  # GitHub OIDC configuration
  oidc_providers      = ["github"]
  github_repositories = ["your-github-repo-name"]  # Your repo name
  github_environments = ["development"]  # Create these in GitHub

  # Project metadata
  business_unit          = "HMPPS"  # Or your unit
  application            = "Your Project Name"
  is_production          = false  # Set to true for prod namespaces
  team_name              = "your-team-name"
  namespace              = var.namespace
  environment_name       = var.environment
  infrastructure_support = "your-team@justice.gov.uk"

  enable_irsa = true  # Enable Kubernetes IRSA for pods
}
```

#### 1c. Submit Pull Request

1. Create a PR in cloud-platform-environments repo
2. Cloud Platform team reviews and merges
3. Infrastructure is automatically provisioned (~5-10 minutes)
4. You receive credentials via Kubernetes secrets and ConfigMaps

**Reference:** See [cloud-platform-environments](https://github.com/ministryofjustice/cloud-platform-environments/tree/main/namespaces/live.cloud-platform.service.justice.gov.uk) for examples

---

### 2. GitHub Configuration

#### 2a. Create GitHub Environments

In your GitHub repository Settings → Environments, create:

- `development`
- `preproduction` (optional)
- `production`

These match the `github_environments` variable in your Cloud Platform ECR config.

#### 2b. Add GitHub Secrets

In your GitHub repository Settings → Secrets and variables → Actions:

**Secrets** (automatically populated by Cloud Platform):
```
ECR_ROLE_TO_ASSUME       = (provided by Cloud Platform)
KUBE_NAMESPACE           = (provided by Cloud Platform)
KUBE_CLUSTER             = (provided by Cloud Platform)
KUBE_CERT                = (provided by Cloud Platform)
KUBE_TOKEN               = (provided by Cloud Platform)
```

**Variables** (Cloud Platform provides defaults, customize as needed):
```
ECR_REGION               = eu-west-2
ECR_REPOSITORY           = (same as namespace name or specified in config)
APP_NAME                 = your-project-name
APP_HOST                 = your-app.cloud-platform.service.justice.gov.uk
CERT_SECRET_NAME         = your-app-tls
```

#### 2d. Customize Workflows

The workflows are ready to use with minimal customisation:

1. **`.github/workflows/docker-publish.yml`** - Already configured, no changes needed
2. **`.github/workflows/docker-build-push-template.yml`** - Already configured, no changes needed
3. **`.github/workflows/deploy-to-environment.yml`** - Customise if you need manual deployment

For most projects, **you don't need to modify the workflows** - they work with the Cloud Platform setup.

---

### 3. Kubernetes Configuration

The Cloud Platform automatically creates:
- Kubernetes namespace
- Service accounts with IRSA
- IAM roles and policies
- Network policies
- TLS certificates

#### 3a. Customize Kubernetes Manifests

In the `deployments/templates/` folder, customize these files for your application:

- **`deployment.yml`**: Update image, resource limits, health checks, environment variables
- **`service.yml`**: Adjust ports and service type
- **`ingress.yml`**: Update hostname (use cloud-platform subdomain)
- **`networkpolicy.yml`**: Configure allowed traffic (Cloud Platform defaults are restrictive)
- **`serviceaccount.yml`**: Service account for your application pods
- **`clusterrole.yml`**: (Optional) RBAC permissions your app needs
- **`clusterrolebinding.yml`**: (Optional) Binds ClusterRole to ServiceAccount

Example customization for your application:

```yaml
# deployments/templates/deployment.yml

containers:
- name: app
  image: ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG}

  # Customize ports for your app
  ports:
  - containerPort: 8000

  # Set environment variables
  env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: app-secrets  # Create this Secret in Cloud Platform namespace
        key: database-url

  # Customize resource limits
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

#### 3b. Use Cloud Platform Subdomain

For ingress, use the Cloud Platform domain:

```yaml
# deployments/templates/ingress.yml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: your-app
  namespace: ${KUBE_NAMESPACE}
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"

spec:
  tls:
  - hosts:
    - your-app.cloud-platform.service.justice.gov.uk  # Use this format
    secretName: your-app-tls

  rules:
  - host: your-app.cloud-platform.service.justice.gov.uk
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: your-app
            port:
              name: http
```

---

## Workflow Triggers

### `docker-publish.yml`

Automatically runs:
- **On PR**: Builds image, pushes to dev ECR
- **On push to main**: Builds image, pushes to both dev and production ECR

### `deploy-to-environment.yml`

Manual trigger (Workflow Dispatch):
- Go to Actions → "Deploy to Environment"
- Select environment (dev, preprod, prod)
- Specify version to deploy (git SHA, tag, or image tag)

---

## How It Works: Image Tagging

Images are tagged with the **git commit SHA**:

```
123456789abcdef@latest
         ↑
    First 7 chars of git SHA
```

Benefits:
- Every image is uniquely identified
- You can trace image back to exact git commit
- Deterministic deployments

Example ECR image:
```
123456789012.dkr.ecr.eu-west-2.amazonaws.com/your-project:abc123d
```

---

## Troubleshooting

### Docker Build Fails
- Check Dockerfile syntax
- Verify all dependencies are in `pyproject.toml`
- Check file permissions in `docker-compose build`

### ECR Push Fails
- Verify AWS credentials/OIDC setup
- Check ECR repository exists and policy allows push
- Check `ECR_ROLE_TO_ASSUME` secret is correct
- Check `ECR_REPOSITORY` variable is correct

### Kubernetes Deployment Fails
- Verify `KUBE_CERT`, `KUBE_TOKEN`, `KUBE_NAMESPACE` secrets
- Check Kubernetes manifests are valid: `kubectl apply --dry-run=client -f deployments/templates/`
- Verify service account and RBAC permissions
- Check `APP_HOST` and other variables are set

### Pods Won't Start
- Check logs: `kubectl logs -n <namespace> <pod-name>`
- Check pod status: `kubectl describe pod -n <namespace> <pod-name>`
- Verify image exists in ECR and is accessible
- Check resource requests/limits

---

## Environment-Specific Configuration

The template supports three environments. Customize for your needs:

### Development
- Automatic deployment on PR and main push
- Lower resource limits
- Enhanced logging/debugging

### Preproduction
- Manual deployment
- Matches production configuration
- Used for testing before prod

### Production
- Manual deployment (requires approval)
- Higher resource limits
- Restricted access

---

## Security Considerations

**Best Practices Included:**
- AWS OIDC authentication (no static credentials)
- Network policies to restrict traffic
- Non-root container security context
- Read-only root filesystem
- Resource limits
- Health checks (liveness/readiness)

**Additional Hardening (Do These):**
- Enable ECR image scanning
- Set up pod security standards
- Use private ECR repositories
- Implement network policies with IP allowlist
- Rotate service account tokens regularly
- Monitor pod logs and events
- Use Secrets for sensitive data (not ConfigMaps)

---

## Next Steps

1. **Set up AWS ECR and OIDC** (work with your infrastructure team)
2. **Add secrets/variables to GitHub** using the setup guide above
3. **Customize Kubernetes manifests** in `deployments/templates/`
4. **Test locally** with Docker Compose:
   ```bash
   docker-compose build
   docker-compose up
   ```
5. **Create a test PR** to trigger the workflow
6. **Monitor the GitHub Actions run** and check ECR for the built image
7. **Test manual deployment** (optional)

---

## Additional Resources

- [AWS ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [cert-manager Documentation](https://cert-manager.io/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
