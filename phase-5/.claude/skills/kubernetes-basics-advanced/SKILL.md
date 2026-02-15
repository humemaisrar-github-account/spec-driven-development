---
name: kubernetes-basics-advanced
description: Generate Kubernetes YAML manifests for deploying microservices applications with Dapr integration. Create Deployments, Services, HPAs, Namespaces, and other Kubernetes resources following best practices for scalable, production-ready deployments.
---

# Kubernetes Manifest & Deployment Manager

## Overview
Generate Kubernetes YAML manifests for Phase 5 microservices applications with Dapr integration. This skill covers both basic and advanced Kubernetes concepts for deploying scalable, production-ready applications.

## Core Capabilities

### 1. Deployments with Dapr Sidecar Integration
Create Deployments with proper Dapr sidecar annotations for service invocation, pub/sub, state management, and secrets.

```yaml
# kubernetes/deployments/chat-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-api
  labels:
    app: chat-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chat-api
  template:
    metadata:
      labels:
        app: chat-api
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-api"
        dapr.io/app-port: "8000"
        dapr.io/config: "app-config"
        dapr.io/app-protocol: "http"
    spec:
      containers:
      - name: chat-api
        image: your-registry/chat-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HOST
          value: "localhost"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### 2. Service Definitions
Create appropriate Services for internal and external communication.

```yaml
# kubernetes/services/chat-api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: chat-api-service
  labels:
    app: chat-api
spec:
  type: ClusterIP
  selector:
    app: chat-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### 3. Horizontal Pod Autoscaler (HPA)
Configure automatic scaling based on CPU and memory metrics.

```yaml
# kubernetes/hpa/chat-api-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chat-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chat-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 4. Namespace Configuration
Organize resources in dedicated namespaces.

```yaml
# kubernetes/namespaces/todo-app-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    name: todo-app
```

### 5. Advanced Configurations

#### ConfigMaps and Secrets
```yaml
# kubernetes/configmaps/app-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: todo-app
data:
  config.json: |
    {
      "loggingLevel": "info",
      "maxRetries": 3
    }
```

#### Network Policies
```yaml
# kubernetes/network-policies/chat-api-netpol.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: chat-api-netpol
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: chat-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: todo-app
    ports:
    - protocol: TCP
      port: 8000
```

## Deployment Strategy

### 1. Prerequisites
- Kubernetes cluster (Minikube, Kind, or cloud provider)
- Dapr installed in the cluster
- Container images pushed to registry

### 2. Apply Order
1. Namespaces
2. ConfigMaps/Secrets
3. Deployments
4. Services
5. HPAs
6. Network Policies

### 3. Deployment Commands
```bash
# Apply all manifests in order
kubectl apply -f kubernetes/namespaces/
kubectl apply -f kubernetes/configmaps/
kubectl apply -f kubernetes/deployments/
kubectl apply -f kubernetes/services/
kubectl apply -f kubernetes/hpa/
kubectl apply -f kubernetes/network-policies/

# Verify deployment
kubectl get pods -n todo-app
kubectl get services -n todo-app
kubectl get hpa -n todo-app
```

## Dapr Integration Best Practices

### 1. Sidecar Annotations
Always include these annotations in your Deployments:
- `dapr.io/enabled: "true"`
- `dapr.io/app-id: "<unique-app-id>"`
- `dapr.io/app-port: "<app-port>"`
- `dapr.io/config: "<config-name>"` (optional)
- `dapr.io/app-protocol: "http"` (or grpc)

### 2. Component References
Reference Dapr components in your application code using the app-id specified in annotations.

## Security Considerations
- Use least-privilege RBAC permissions
- Enable network policies
- Store secrets securely using Kubernetes secrets or external secret stores
- Regularly scan container images for vulnerabilities

## Monitoring and Observability
- Enable Dapr sidecar metrics
- Configure health checks (liveness/readiness probes)
- Set up centralized logging
- Monitor resource utilization

## Troubleshooting
- Check Dapr sidecar injection: `kubectl describe pod <pod-name>`
- View Dapr logs: `kubectl logs <pod-name> daprd`
- Verify Dapr placement service connectivity
- Check resource quotas in namespace