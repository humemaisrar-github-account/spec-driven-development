---
name: github-actions-workflow-builder
description: Generate GitHub Actions workflow files for CI/CD pipelines including linting, testing, Docker builds, and Kubernetes deployments. Create production-ready GitHub Actions workflows with proper secrets management and deployment to various platforms (Minikube, AKS, GKE).
---

# GitHub Actions Workflow Builder

## Overview
Generate GitHub Actions workflow files for CI/CD pipelines for Phase 5 microservices applications with proper secrets management and deployment to various platforms.

## Core Workflows

### 1. CI Build Workflow
Lint, test, and build Docker images for all services.

```yaml
# .github/workflows/ci-build.yaml
name: CI Build

on:
  push:
    branches: [ develop, feature/* ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ -v

  build-docker-images:
    needs: lint-and-test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [chat-api, recurring-task-service, notification-service]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata for ${{ matrix.service }}
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{date 'YYYYMMDD'}}-
    
    - name: Build and push ${{ matrix.service }} image
      uses: docker/build-push-action@v5
      with:
        context: ./services/${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### 2. CD Deploy Workflow
Deploy to Minikube or cloud Kubernetes clusters on main branch pushes.

```yaml
# .github/workflows/cd-deploy.yaml
name: CD Deploy

on:
  push:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-minikube:
    runs-on: ubuntu-latest
    if: ${{ vars.USE_MINIKUBE == 'true' }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker
      uses: docker/setup-docker-action@v3
    
    - name: Set up Minikube
      uses: medyagh/setup-minikube@master
      with:
        driver: docker
        kubernetes-version: v1.28.3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Update image tags in Kubernetes manifests
      run: |
        sed -i "s|your-registry/chat-api:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-chat-api:${{ github.sha }}|g" kubernetes/full-deployment-set/chat-api/deployment.yaml
        sed -i "s|your-registry/recurring-task-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-recurring-task-service:${{ github.sha }}|g" kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
        sed -i "s|your-registry/notification-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-notification-service:${{ github.sha }}|g" kubernetes/full-deployment-set/notification-service/deployment.yaml
    
    - name: Apply Kubernetes manifests
      run: |
        kubectl apply -f kubernetes/full-deployment-set/secrets/
        kubectl apply -f kubernetes/full-deployment-set/rbac/
        kubectl apply -f kubernetes/full-deployment-set/chat-api/
        kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
        kubectl apply -f kubernetes/full-deployment-set/notification-service/
    
    - name: Wait for deployments to be ready
      run: |
        kubectl rollout status deployment/chat-api -n todo-app --timeout=300s
        kubectl rollout status deployment/recurring-task-service -n todo-app --timeout=300s
        kubectl rollout status deployment/notification-service -n todo-app --timeout=300s

  deploy-azure-aks:
    runs-on: ubuntu-latest
    if: ${{ vars.USE_AKS == 'true' }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v2
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'
    
    - name: Get AKS credentials
      run: |
        az aks get-credentials --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} --name ${{ secrets.AZURE_CLUSTER_NAME }}
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Update image tags in Kubernetes manifests
      run: |
        sed -i "s|your-registry/chat-api:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-chat-api:${{ github.sha }}|g" kubernetes/full-deployment-set/chat-api/deployment.yaml
        sed -i "s|your-registry/recurring-task-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-recurring-task-service:${{ github.sha }}|g" kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
        sed -i "s|your-registry/notification-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-notification-service:${{ github.sha }}|g" kubernetes/full-deployment-set/notification-service/deployment.yaml
    
    - name: Deploy to AKS
      run: |
        kubectl apply -f kubernetes/full-deployment-set/secrets/
        kubectl apply -f kubernetes/full-deployment-set/rbac/
        kubectl apply -f kubernetes/full-deployment-set/chat-api/
        kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
        kubectl apply -f kubernetes/full-deployment-set/notification-service/
    
    - name: Wait for deployments to be ready
      run: |
        kubectl rollout status deployment/chat-api -n todo-app --timeout=300s
        kubectl rollout status deployment/recurring-task-service -n todo-app --timeout=300s
        kubectl rollout status deployment/notification-service -n todo-app --timeout=300s

  deploy-google-gke:
    runs-on: ubuntu-latest
    if: ${{ vars.USE_GKE == 'true' }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_CREDENTIALS }}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Get GKE credentials
      run: |
        gcloud container clusters get-credentials ${{ secrets.GKE_CLUSTER_NAME }} --zone ${{ secrets.GKE_ZONE }} --project ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Update image tags in Kubernetes manifests
      run: |
        sed -i "s|your-registry/chat-api:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-chat-api:${{ github.sha }}|g" kubernetes/full-deployment-set/chat-api/deployment.yaml
        sed -i "s|your-registry/recurring-task-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-recurring-task-service:${{ github.sha }}|g" kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
        sed -i "s|your-registry/notification-service:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-notification-service:${{ github.sha }}|g" kubernetes/full-deployment-set/notification-service/deployment.yaml
    
    - name: Deploy to GKE
      run: |
        kubectl apply -f kubernetes/full-deployment-set/secrets/
        kubectl apply -f kubernetes/full-deployment-set/rbac/
        kubectl apply -f kubernetes/full-deployment-set/chat-api/
        kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
        kubectl apply -f kubernetes/full-deployment-set/notification-service/
    
    - name: Wait for deployments to be ready
      run: |
        kubectl rollout status deployment/chat-api -n todo-app --timeout=300s
        kubectl rollout status deployment/recurring-task-service -n todo-app --timeout=300s
        kubectl rollout status deployment/notification-service -n todo-app --timeout=300s
```

### 3. Security Scan Workflow
Scan for vulnerabilities in code and container images.

```yaml
# .github/workflows/security-scan.yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Mondays at 2 AM

jobs:
  codeql-analysis:
    name: CodeQL Analysis
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2

  container-scan:
    name: Container Vulnerability Scan
    runs-on: ubuntu-latest
    needs: codeql-analysis

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner in repo mode
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
```

### 4. Dapr Runtime Setup Workflow
Install and configure Dapr in the target cluster.

```yaml
# .github/workflows/dapr-setup.yaml
name: Dapr Setup

on:
  workflow_dispatch:
  push:
    branches: [ main ]
    paths:
      - 'dapr-components/**'

jobs:
  setup-dapr:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        cluster: [minikube, aks, gke]
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Dapr CLI
      uses: dapr/setup-dapr@v3
      with:
        dapr-cli-version: 'latest'
        dapr-runtime-version: 'latest'
    
    - name: Install Dapr on Minikube
      if: matrix.cluster == 'minikube'
      run: |
        minikube start
        dapr init -k
    
    - name: Install Dapr on AKS
      if: matrix.cluster == 'aks'
      run: |
        az aks get-credentials --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} --name ${{ secrets.AZURE_CLUSTER_NAME }}
        dapr init -k
    
    - name: Install Dapr on GKE
      if: matrix.cluster == 'gke'
      run: |
        gcloud container clusters get-credentials ${{ secrets.GKE_CLUSTER_NAME }} --zone ${{ secrets.GKE_ZONE }} --project ${{ secrets.GCP_PROJECT_ID }}
        dapr init -k
    
    - name: Apply Dapr Components
      run: |
        kubectl apply -f dapr-components/
    
    - name: Verify Dapr Installation
      run: |
        kubectl get pods -n dapr-system
        dapr status -k
```

## Secrets Management

### Required Secrets for GitHub Repository

Add these secrets to your GitHub repository under Settings > Secrets and variables > Actions:

```
# Docker Registry
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
GITHUB_TOKEN (automatically provided)

# Kubernetes Clusters
KUBE_CONFIG_DATA (base64 encoded kubeconfig)
AZURE_CREDENTIALS (JSON format)
AZURE_RESOURCE_GROUP
AZURE_CLUSTER_NAME
GCP_CREDENTIALS (JSON format)
GCP_PROJECT_ID
GKE_CLUSTER_NAME
GKE_ZONE

# Database Credentials
NEON_DB_CONNECTION_STRING
REDBOOK_USERNAME
REDBOOK_PASSWORD

# Other Services
SLACK_WEBHOOK_URL (for notifications)
```

### Required Variables for GitHub Repository

Add these variables to your GitHub repository under Settings > Secrets and variables > Actions:

```
# Deployment Configuration
USE_MINIKUBE: true/false
USE_AKS: true/false
USE_GKE: true/false

# Image Registry
CONTAINER_REGISTRY: ghcr.io or docker.io

# Environment
ENVIRONMENT: dev/staging/prod
NAMESPACE: todo-app
```

## Deployment Strategies

### 1. Blue-Green Deployment
```yaml
# .github/workflows/blue-green-deploy.yaml
name: Blue-Green Deployment

on:
  push:
    branches: [ main ]

jobs:
  blue-green-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Determine active deployment
      id: active
      run: |
        ACTIVE_DEPLOYMENT=$(kubectl get service/todo-app-service -o jsonpath='{.spec.selector.deployment}')
        echo "ACTIVE_DEPLOYMENT=$ACTIVE_DEPLOYMENT" >> $GITHUB_OUTPUT
        
    - name: Deploy to inactive environment
      run: |
        if [ "${{ steps.active.outputs.ACTIVE_DEPLOYMENT }}" = "todo-app-blue" ]; then
          # Deploy green
          sed -i 's/todo-app-blue/todo-app-green/g' kubernetes/deployment-green.yaml
          kubectl apply -f kubernetes/deployment-green.yaml
          INACTIVE_ENV=green
        else
          # Deploy blue
          sed -i 's/todo-app-green/todo-app-blue/g' kubernetes/deployment-blue.yaml
          kubectl apply -f kubernetes/deployment-blue.yaml
          INACTIVE_ENV=blue
        fi
        
    - name: Wait for new deployment to be ready
      run: |
        kubectl rollout status deployment/todo-app-${{ env.INACTIVE_ENV }} --timeout=300s
    
    - name: Switch traffic to new deployment
      run: |
        kubectl patch service/todo-app-service -p '{"spec":{"selector":{"deployment":"todo-app-${{ env.INACTIVE_ENV }}"}}}'
    
    - name: Scale down old deployment
      run: |
        if [ "${{ env.INACTIVE_ENV }}" = "green" ]; then
          kubectl scale deployment/todo-app-blue --replicas=0
        else
          kubectl scale deployment/todo-app-green --replicas=0
        fi
```

## Notifications

### Slack Notification Workflow
```yaml
# .github/workflows/notifications.yaml
name: Notifications

on:
  workflow_run:
    workflows: [ "CI Build", "CD Deploy" ]
    types: [ completed ]

jobs:
  notify:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion != 'skipped' }}
    steps:
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
        text: |
          ${{ github.event.workflow_run.name }} ${{ github.event.workflow_run.conclusion == 'success' && 'succeeded' || 'failed' }}!
          Repo: ${{ github.repository }}
          Branch: ${{ github.ref_name }}
          Commit: ${{ github.sha }}
          Link: ${{ github.event.workflow_run.html_url }}
```

## Best Practices

### 1. Security
- Never hardcode secrets in workflow files
- Use GitHub secrets for sensitive information
- Limit permissions to minimum required
- Scan for vulnerabilities regularly

### 2. Reliability
- Use specific action versions (not @main)
- Implement proper error handling
- Add timeouts for operations
- Use matrix strategies for testing

### 3. Efficiency
- Use caching for dependencies
- Parallelize independent jobs
- Clean up resources after deployment
- Use conditional execution

### 4. Monitoring
- Add health checks after deployment
- Implement rollback mechanisms
- Set up notifications for failures
- Monitor deployment metrics