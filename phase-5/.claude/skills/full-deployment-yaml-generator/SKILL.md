---
name: full-deployment-yaml-generator
description: Generate complete Kubernetes YAML sets for deployments, services, HPAs, secrets, and Helm values overrides. Create production-ready deployment configurations with proper Dapr integration, health checks, and security practices for event-driven microservices applications.
---

# Full Deployment YAML Generator

## Overview
Generate complete Kubernetes YAML sets for Phase 5 microservices applications with Dapr integration, health checks, and security best practices.

## Core Components

### 1. Chat API Deployment with Dapr Sidecar
Complete deployment for the main Chat API service.

```yaml
# kubernetes/full-deployment-set/chat-api/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-api
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-chatbot
      component: chat-api
  template:
    metadata:
      labels:
        app: todo-chatbot
        component: chat-api
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-api"
        dapr.io/app-port: "8000"
        dapr.io/config: "app-config"
        dapr.io/app-protocol: "http"
        dapr.io/log-as-json: "true"
    spec:
      containers:
      - name: chat-api
        image: your-registry/chat-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: DAPR_GRPC_ENDPOINT
          value: "http://localhost:50001"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neon-db-secret
              key: connectionString
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      serviceAccountName: chat-api-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
```

### 2. Chat API Service Definition
Service for exposing the Chat API internally and externally.

```yaml
# kubernetes/full-deployment-set/chat-api/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: chat-api-service
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
spec:
  type: ClusterIP
  selector:
    app: todo-chatbot
    component: chat-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  - protocol: TCP
    port: 9090
    targetPort: 9090
    name: metrics
```

### 3. Chat API Horizontal Pod Autoscaler
HPA for automatic scaling based on CPU and memory metrics.

```yaml
# kubernetes/full-deployment-set/chat-api/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chat-api-hpa
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 4. Recurring Task Service Deployment
Deployment for the RecurringTaskService with Dapr integration.

```yaml
# kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: recurring-task-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-chatbot
      component: recurring-task-service
  template:
    metadata:
      labels:
        app: todo-chatbot
        component: recurring-task-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-task-service"
        dapr.io/app-port: "8000"
        dapr.io/config: "app-config"
        dapr.io/app-protocol: "http"
        dapr.io/log-as-json: "true"
    spec:
      containers:
      - name: recurring-task-service
        image: your-registry/recurring-task-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: DAPR_GRPC_ENDPOINT
          value: "http://localhost:50001"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      serviceAccountName: recurring-task-service-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
```

### 5. Recurring Task Service Service
Service for the RecurringTaskService.

```yaml
# kubernetes/full-deployment-set/recurring-task-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: recurring-task-service
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: recurring-task-service
spec:
  type: ClusterIP
  selector:
    app: todo-chatbot
    component: recurring-task-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
```

### 6. Notification Service Deployment
Deployment for the NotificationService with Dapr integration.

```yaml
# kubernetes/full-deployment-set/notification-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: notification-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-chatbot
      component: notification-service
  template:
    metadata:
      labels:
        app: todo-chatbot
        component: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8000"
        dapr.io/config: "app-config"
        dapr.io/app-protocol: "http"
        dapr.io/log-as-json: "true"
    spec:
      containers:
      - name: notification-service
        image: your-registry/notification-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: DAPR_GRPC_ENDPOINT
          value: "http://localhost:50001"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      serviceAccountName: notification-service-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
```

### 7. Notification Service Service
Service for the NotificationService.

```yaml
# kubernetes/full-deployment-set/notification-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: notification-service
spec:
  type: ClusterIP
  selector:
    app: todo-chatbot
    component: notification-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
```

### 8. Kubernetes Secrets for Neon Database
Secure storage for Neon database credentials.

```yaml
# kubernetes/full-deployment-set/secrets/neon-db-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: neon-db-secret
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: database
type: Opaque
data:
  connectionString: <base64-encoded-neon-connection-string>
  # Example: "host=ep-xxx.neon.tech user=xxx password=xxx dbname=xxx sslmode=require"
```

### 9. Kubernetes Secrets for Redpanda
Secure storage for Redpanda credentials.

```yaml
# kubernetes/full-deployment-set/secrets/redpanda-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: redpanda-secret
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: messaging
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  bootstrap-servers: <base64-encoded-bootstrap-url>
```

### 10. Service Accounts
Service accounts for each component with minimal required permissions.

```yaml
# kubernetes/full-deployment-set/rbac/chat-api-sa.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: chat-api-sa
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: chat-api-role
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: chat-api-rolebinding
  namespace: todo-app
  labels:
    app: todo-chatbot
    component: chat-api
subjects:
- kind: ServiceAccount
  name: chat-api-sa
  namespace: todo-app
roleRef:
  kind: Role
  name: chat-api-role
  apiGroup: rbac.authorization.k8s.io
```

### 11. Helm Values Override
Override values for extending Phase 4 Helm chart.

```yaml
# kubernetes/full-deployment-set/helm-values-override.yaml
# Override values for extending Phase 4 Helm chart
global:
  imageRegistry: your-registry
  imagePullSecrets: []
  storageClass: ""

# Chat API Configuration
chatApi:
  replicaCount: 3
  image:
    repository: chat-api
    pullPolicy: IfNotPresent
    tag: latest
  service:
    type: ClusterIP
    port: 80
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi
  dapr:
    enabled: true
    appId: "chat-api"
    appPort: 8000
    config: "app-config"
  healthChecks:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      initialDelaySeconds: 5
      periodSeconds: 5

# Recurring Task Service Configuration
recurringTaskService:
  replicaCount: 2
  image:
    repository: recurring-task-service
    pullPolicy: IfNotPresent
    tag: latest
  service:
    type: ClusterIP
    port: 80
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  dapr:
    enabled: true
    appId: "recurring-task-service"
    appPort: 8000
    config: "app-config"
  healthChecks:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      initialDelaySeconds: 5
      periodSeconds: 5

# Notification Service Configuration
notificationService:
  replicaCount: 2
  image:
    repository: notification-service
    pullPolicy: IfNotPresent
    tag: latest
  service:
    type: ClusterIP
    port: 80
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  dapr:
    enabled: true
    appId: "notification-service"
    appPort: 8000
    config: "app-config"
  healthChecks:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      initialDelaySeconds: 5
      periodSeconds: 5

# HPA Configuration
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

# Security Context
securityContext:
  enabled: true
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000

# Node Selector (optional)
nodeSelector: {}

# Tolerations (optional)
tolerations: []

# Affinity (optional)
affinity: {}
```

## Deployment Instructions

### 1. Apply Secrets First
```bash
kubectl apply -f kubernetes/full-deployment-set/secrets/
```

### 2. Apply RBAC Resources
```bash
kubectl apply -f kubernetes/full-deployment-set/rbac/
```

### 3. Apply Services
```bash
kubectl apply -f kubernetes/full-deployment-set/chat-api/service.yaml
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/service.yaml
kubectl apply -f kubernetes/full-deployment-set/notification-service/service.yaml
```

### 4. Apply Deployments
```bash
kubectl apply -f kubernetes/full-deployment-set/chat-api/deployment.yaml
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
kubectl apply -f kubernetes/full-deployment-set/notification-service/deployment.yaml
```

### 5. Apply HPAs
```bash
kubectl apply -f kubernetes/full-deployment-set/chat-api/hpa.yaml
```

## Security Best Practices

### 1. Minimal RBAC Permissions
- Grant only necessary permissions to service accounts
- Use Roles/RolesBindings instead of ClusterRoles where possible

### 2. Non-root Containers
- Run containers as non-root users
- Set appropriate security contexts

### 3. Secret Management
- Store sensitive data in Kubernetes secrets
- Use secretKeyRef for referencing secrets in deployments

### 4. Network Security
- Use NetworkPolicies to restrict traffic between services
- Enable TLS for all inter-service communication

## Health Checks

### Liveness Probes
- Detect when a container is dead and needs restart
- Use endpoints that check the application's core functionality

### Readiness Probes
- Determine when a container is ready to serve traffic
- Prevent traffic routing to unhealthy containers

## Monitoring and Observability

### Metrics Endpoints
- Expose Prometheus metrics endpoints
- Configure service monitors for metric collection

### Logging
- Configure structured logging
- Forward logs to centralized logging solution

## Troubleshooting

### Common Issues:
1. **Pods not starting**: Check image pull secrets and registry access
2. **Health check failures**: Verify liveness/readiness probe configurations
3. **Dapr sidecar issues**: Check Dapr runtime installation and annotations
4. **Resource constraints**: Verify resource requests/limits match cluster capacity

### Useful Commands:
```bash
# Check pod status
kubectl get pods -n todo-app

# Check service status
kubectl get svc -n todo-app

# Check HPA status
kubectl get hpa -n todo-app

# View pod logs
kubectl logs <pod-name> -n todo-app

# Check Dapr sidecar logs
kubectl logs <pod-name> daprd -n todo-app
```

## Integration with Dapr

All deployments include proper Dapr annotations for:
- Service invocation
- State management
- Pub/Sub messaging
- Secret management
- Distributed tracing