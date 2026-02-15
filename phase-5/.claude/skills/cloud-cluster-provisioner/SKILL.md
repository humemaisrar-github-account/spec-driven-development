---
name: cloud-cluster-provisioner
description: Generate step-by-step commands for provisioning cloud Kubernetes clusters including Azure AKS, Google GKE, and Oracle OKE. Create complete setup guides with kubectl connection and configuration for production-ready cloud deployments.
---

# Cloud Cluster Provisioner

## Overview
Generate step-by-step commands for provisioning cloud Kubernetes clusters for Phase 5 microservices applications with Dapr integration.

## Core Components

### 1. Azure AKS Setup Guide
Complete guide for creating and connecting to Azure AKS cluster.

```markdown
# cloud-setup/azure-aks.md

# Azure AKS Cluster Setup Guide

## Prerequisites
- Azure account with subscription
- Azure CLI installed (`az --version` to verify)
- kubectl installed (`kubectl version` to verify)
- Free credit or pay-as-you-go account

## Step 1: Login to Azure
```bash
az login
```

## Step 2: Set Subscription
```bash
# List available subscriptions
az account list --output table

# Set your subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

## Step 3: Create Resource Group
```bash
# Create resource group
az group create --name todo-app-rg --location eastus
```

## Step 4: Create AKS Cluster
```bash
# Create AKS cluster with 2 nodes (minimum for production)
az aks create \
  --resource-group todo-app-rg \
  --name todo-app-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --kubernetes-version 1.28 \
  --enable-managed-identity \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 5
```

## Step 5: Connect kubectl to AKS
```bash
# Get AKS credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-aks

# Verify connection
kubectl cluster-info
kubectl get nodes
```

## Step 6: Verify Dapr Installation
```bash
# Install Dapr CLI if not already installed
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Dapr to AKS cluster
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system
```

## Step 7: Set Up Azure Container Registry (Optional but Recommended)
```bash
# Create ACR
az acr create --resource-group todo-app-rg --name todoappacr --sku Basic

# Attach ACR to AKS
az aks update --name todo-app-aks --resource-group todo-app-rg --attach-acr todoappacr

# Login to ACR
az acr login --name todoappacr
```

## Step 8: Deploy Application
```bash
# Apply your Kubernetes manifests
kubectl apply -f kubernetes/full-deployment-set/secrets/
kubectl apply -f kubernetes/full-deployment-set/rbac/
kubectl apply -f kubernetes/full-deployment-set/chat-api/
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
kubectl apply -f kubernetes/full-deployment-set/notification-service/

# Verify deployment
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

## Cleanup (When Done)
```bash
# Delete AKS cluster and resource group
az group delete --name todo-app-rg --yes --no-wait
```

## Cost Optimization Tips
- Use Virtual Nodes for burst workloads
- Enable cluster autoscaler
- Use Spot VMs for non-critical workloads
- Monitor costs with Azure Cost Management
```

### 2. Google GKE Setup Guide
Complete guide for creating and connecting to Google GKE cluster.

```markdown
# cloud-setup/gke.md

# Google GKE Cluster Setup Guide

## Prerequisites
- Google Cloud account with billing enabled
- Google Cloud SDK installed (`gcloud version` to verify)
- kubectl installed (`kubectl version` to verify)
- Free trial credit or billing account

## Step 1: Login to Google Cloud
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## Step 2: Enable Required APIs
```bash
# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 3: Set Compute Zone
```bash
# Set default compute zone (choose a region near you)
gcloud config set compute/zone us-central1-a
```

## Step 4: Create GKE Cluster
```bash
# Create GKE cluster with 2 nodes
gcloud container clusters create todo-app-gke \
  --num-nodes=2 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --machine-type=e2-medium \
  --disk-size=20GB \
  --enable-ip-alias \
  --enable-shielded-nodes \
  --shielded-secure-boot \
  --shielded-integrity-monitoring
```

## Step 5: Connect kubectl to GKE
```bash
# Get GKE credentials
gcloud container clusters get-credentials todo-app-gke

# Verify connection
kubectl cluster-info
kubectl get nodes
```

## Step 6: Verify Dapr Installation
```bash
# Install Dapr CLI if not already installed
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Dapr to GKE cluster
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system
```

## Step 7: Set Up Google Container Registry (Optional but Recommended)
```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Or for specific regions:
gcloud auth configure-docker gcr.io,us.gcr.io,eu.gcr.io,asia.gcr.io
```

## Step 8: Deploy Application
```bash
# Apply your Kubernetes manifests
kubectl apply -f kubernetes/full-deployment-set/secrets/
kubectl apply -f kubernetes/full-deployment-set/rbac/
kubectl apply -f kubernetes/full-deployment-set/chat-api/
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
kubectl apply -f kubernetes/full-deployment-set/notification-service/

# Verify deployment
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

## Step 9: Configure Cloud Build (Optional)
```bash
# Create a build trigger
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/todo-app .
```

## Cleanup (When Done)
```bash
# Delete GKE cluster
gcloud container clusters delete todo-app-gke --zone=us-central1-a
```

## Cost Optimization Tips
- Use preemptible nodes for non-critical workloads
- Enable cluster autoscaling
- Use regional clusters for high availability
- Monitor costs with Google Cloud Billing
```

### 3. Oracle OKE Setup Guide
Complete guide for creating and connecting to Oracle OKE cluster (always free tier).

```markdown
# cloud-setup/oracle-oke.md

# Oracle OKE Cluster Setup Guide (Always Free Tier)

## Prerequisites
- Oracle Cloud account (free tier eligible)
- Oracle Cloud Infrastructure CLI installed
- kubectl installed (`kubectl version` to verify)
- Terraform installed (optional but recommended)

## Step 1: Login to Oracle Cloud
```bash
# Download and install OCI CLI
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh -o install.sh
bash install.sh

# Configure OCI CLI
oci setup config
```

## Step 2: Create Compartment (Optional)
```bash
# Create a compartment for your resources
oci iam compartment create --compartment-id YOUR_TENANCY_OCID --name todo-app-compartment --description "Compartment for Todo App"
```

## Step 3: Create VCN and Subnets
```bash
# Create VCN
oci network vcn create --compartment-id YOUR_COMPARTMENT_OCID --display-name todo-app-vcn --cidr-block 10.0.0.0/16

# Create public subnet
oci network subnet create --compartment-id YOUR_COMPARTMENT_OCID --availability-domain-1 YOUR_AD1 --vcn-id YOUR_VCN_OCID --display-name todo-app-public-subnet --cidr-block 10.0.1.0/24 --route-table-id YOUR_ROUTE_TABLE_ID

# Create private subnet
oci network subnet create --compartment-id YOUR_COMPARTMENT_OCID --availability-domain-1 YOUR_AD1 --vcn-id YOUR_VCN_OCID --display-name todo-app-private-subnet --cidr-block 10.0.2.0/24
```

## Step 4: Create OKE Cluster
```bash
# Create OKE cluster using the free tier eligible configuration
oci ce cluster create \
  --name todo-app-oke \
  --kubernetes-version v1.28.2 \
  --vcn-id YOUR_VCN_OCID \
  --service-lb-subnet-ids YOUR_PUBLIC_SUBNET_OCID \
  --dashboard-enabled false \
  --compartment-id YOUR_COMPARTMENT_OCID \
  --endpoint-config "{\"isPublicIpEnabled\": true}"

# Get the cluster OCID from the response
```

## Step 5: Create Node Pool
```bash
# Create a node pool with free tier eligible shape
oci ce node-pool create \
  --name todo-app-nodepool \
  --cluster-id YOUR_CLUSTER_OCID \
  --compartment-id YOUR_COMPARTMENT_OCID \
  --vcn-id YOUR_VCN_OCID \
  --subnet-ids YOUR_PRIVATE_SUBNET_OCID \
  --kubernetes-version v1.28.2 \
  --node-image-name "Canonical Ubuntu 22.04" \
  --node-shape "VM.Standard.E2.1.Micro" \
  --quantity-per-subnet 1 \
  --quantity-of-subnets 1 \
  --ssh-public-key-file ~/.ssh/id_rsa.pub
```

## Step 6: Connect kubectl to OKE
```bash
# Get cluster kubeconfig
oci ce cluster create-kubeconfig --cluster-id YOUR_CLUSTER_OCID --file ~/.kube/config --region us-phoenix-1

# Verify connection
kubectl cluster-info
kubectl get nodes
```

## Step 7: Verify Dapr Installation
```bash
# Install Dapr CLI if not already installed
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Dapr to OKE cluster
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system
```

## Step 8: Set Up Oracle Cloud Container Registry (Optional)
```bash
# Login to Oracle Cloud Container Registry
docker login fra.ocir.io -u YOUR_TENANCY_NAMESPACE/USERNAME -p "YOUR_AUTH_TOKEN"

# The auth token can be generated in Oracle Cloud Console under User Settings
```

## Step 9: Deploy Application
```bash
# Apply your Kubernetes manifests
kubectl apply -f kubernetes/full-deployment-set/secrets/
kubectl apply -f kubernetes/full-deployment-set/rbac/
kubectl apply -f kubernetes/full-deployment-set/chat-api/
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/
kubectl apply -f kubernetes/full-deployment-set/notification-service/

# Verify deployment
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

## Step 10: Configure Load Balancer (if needed)
```bash
# OKE creates a load balancer automatically, but you can customize it
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: chat-api-loadbalancer
  namespace: todo-app
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: todo-chatbot
    component: chat-api
EOF
```

## Cleanup (When Done)
```bash
# Delete node pool
oci ce node-pool delete --node-pool-id YOUR_NODE_POOL_OCID --force

# Delete cluster
oci ce cluster delete --cluster-id YOUR_CLUSTER_OCID --force

# Delete VCN (after cluster deletion)
oci network vcn delete --vcn-id YOUR_VCN_OCID --force
```

## Oracle Cloud Always Free Tier Benefits
- Always-free VM.Standard.E2.1.Micro instances (1 OCPU, 1 GB memory)
- Always-free load balancers
- Always-free container engine for Kubernetes
- No time limit on free tier resources
- Generous monthly free tier for additional services

## Cost Optimization Tips
- Use VM.Standard.E2.1.Micro for nodes (always free)
- Take advantage of always-free load balancers
- Monitor usage to stay within free tier limits
- Use Oracle Cloud Console to track resource consumption
```

### 4. Cross-Cloud Comparison Guide
Guide comparing the different cloud providers.

```markdown
# cloud-setup/comparison.md

# Cloud Provider Comparison Guide

## Cost Comparison

### Azure AKS
- **Free Tier**: Limited free tier with conditions
- **Pay-as-you-go**: Pay for underlying VMs and storage
- **Free Credits**: $200 credit for first 30 days
- **Recommended**: Good for enterprise workloads

### Google GKE
- **Free Tier**: Limited free tier with conditions
- **Pay-as-you-go**: Pay for underlying VMs and storage
- **Free Credits**: $300 credit for first 90 days
- **Recommended**: Good for container-native applications

### Oracle OKE
- **Always Free**: VM.Standard.E2.1.Micro always free
- **No Time Limit**: Free tier has no expiration
- **Free Services**: Load balancers, container engine always free
- **Recommended**: Best for long-term development and testing

## Performance Comparison

### Azure AKS
- **Strengths**: Strong enterprise integration, hybrid scenarios
- **Performance**: Good performance with premium options
- **Integration**: Excellent with other Azure services

### Google GKE
- **Strengths**: Native Kubernetes experience, Google infrastructure
- **Performance**: Optimized for Kubernetes workloads
- **Integration**: Excellent with Google Cloud services

### Oracle OKE
- **Strengths**: Always free tier, no time pressure
- **Performance**: Good for development and small production workloads
- **Integration**: Good with Oracle ecosystem

## Recommendation for Phase 5

For Phase 5 development and deployment:

1. **Development Phase**: Use Oracle OKE (always free, no time pressure)
2. **Testing Phase**: Use Oracle OKE or Google GKE
3. **Production Phase**: Choose based on enterprise requirements:
   - Azure AKS for Microsoft ecosystem
   - Google GKE for Google Cloud integration
   - Oracle OKE for cost-effective small-scale production

## Migration Between Providers

All three providers use standard Kubernetes, so migration is possible:
- Kubernetes manifests remain the same
- Cloud-specific configurations may need adjustment
- Storage and networking configurations differ
- CI/CD pipelines may need updates
```

### 5. Terraform Automation Scripts
Terraform scripts for automated cluster provisioning.

```hcl
# cloud-setup/terraform/aks-cluster.tf

# Azure AKS Terraform Configuration
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "todo-app-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "todo-app-aks"
}

# Create Resource Group
resource "azurerm_resource_group" "aks_rg" {
  name     = var.resource_group_name
  location = var.location
}

# Create AKS Cluster
resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                = var.cluster_name
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  dns_prefix          = var.cluster_name

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_D2_v2"

    enable_auto_scaling = true
    min_count         = 2
    max_count         = 5
  }

  identity {
    type = "SystemAssigned"
  }

  oms_agent {
    log_analytics_workspace_arm_id = azurerm_log_analytics_workspace.test.id
  }

  tags = {
    Environment = "Phase5"
  }
}

resource "azurerm_log_analytics_workspace" "test" {
  name                = "${var.cluster_name}-analytics"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}
```

```hcl
# cloud-setup/terraform/gke-cluster.tf

# Google GKE Terraform Configuration
variable "project" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "todo-app-gke"
}

# Configure the Google Cloud provider
provider "google" {
  project = var.project
  region  = var.region
}

# Create GKE Cluster
resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project}.svc.id.goog"
  }
}

# Create Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  autoscaling {
    min_node_count = 2
    max_node_count = 5
  }

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 20

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
```

## Best Practices

### 1. Security Best Practices
- Use managed identities where available
- Enable network policies
- Implement RBAC properly
- Use secrets management
- Enable audit logging

### 2. Cost Management
- Monitor resource usage regularly
- Use reserved instances for predictable workloads
- Implement resource quotas
- Use spot/preemptible instances for non-critical workloads

### 3. High Availability
- Use multiple availability zones
- Implement proper backup strategies
- Use load balancers
- Monitor cluster health

### 4. Monitoring and Logging
- Enable cluster monitoring
- Set up alerting
- Implement centralized logging
- Monitor application metrics