---
name: debugging-monitoring-toolkit
description: Generate commands and scripts for debugging and monitoring Kubernetes applications with Dapr integration. Create tools for log analysis, metrics collection, port forwarding, and monitoring setup for event-driven microservices applications.
---

# Debugging & Monitoring Toolkit

## Overview
Generate commands and scripts for debugging and monitoring Kubernetes applications with Dapr integration for Phase 5 microservices applications.

## Core Components

### 1. Full Pod Logs Commands
Commands to view logs from application containers and Dapr sidecars.

```bash
# scripts/debug.sh
#!/bin/bash

# Full Pod Logs Commands
echo "=== Full Pod Logs Commands ==="

# Get all pods in the todo-app namespace
echo "Getting all pods in todo-app namespace..."
kubectl get pods -n todo-app

echo ""
echo "Enter the pod name to view logs:"
read POD_NAME

# View application container logs
echo "=== Application Container Logs ==="
kubectl logs $POD_NAME -n todo-app

echo ""
echo "=== Dapr Sidecar Logs ==="
kubectl logs $POD_NAME -n todo-app -c daprd

echo ""
echo "=== Combined Logs (Application + Dapr) ==="
kubectl logs $POD_NAME -n todo-app --all-containers=true

echo ""
echo "=== Follow Logs (Real-time) ==="
echo "Application logs:"
echo "kubectl logs -f $POD_NAME -n todo-app"
echo ""
echo "Dapr sidecar logs:"
echo "kubectl logs -f $POD_NAME -n todo-app -c daprd"
```

### 2. Dapr-Specific Debug Commands
Commands specifically for Dapr debugging.

```bash
# scripts/dapr-debug.sh
#!/bin/bash

echo "=== Dapr-Specific Debug Commands ==="

# Get Dapr sidecar status
echo "Checking Dapr sidecar status..."
kubectl get pods -n todo-app -o yaml | grep -A 10 -B 10 dapr

echo ""
echo "View Dapr sidecar logs for all pods:"
kubectl logs -l app=todo-chatbot -n todo-app -c daprd

echo ""
echo "Check Dapr components status:"
kubectl get components.dapr.io -A

echo ""
echo "Check Dapr subscriptions:"
kubectl get subscriptions.dapr.io -A

echo ""
echo "Run Dapr dashboard:"
echo "dapr dashboard -k"
echo "Then visit http://localhost:8080"

echo ""
echo "Check Dapr control plane:"
kubectl get pods -n dapr-system
```

### 3. Port Forwarding Commands
Set up port forwarding for debugging and monitoring.

```bash
# scripts/port-forward.sh
#!/bin/bash

echo "=== Port Forwarding Commands ==="

echo "Port forward to Chat API service:"
echo "kubectl port-forward svc/chat-api-service -n todo-app 8080:80"

echo ""
echo "Port forward to Dapr dashboard:"
echo "kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080"

echo ""
echo "Port forward to Prometheus (if deployed):"
echo "kubectl port-forward svc/prometheus-server -n monitoring 9090:80"

echo ""
echo "Port forward to Grafana (if deployed):"
echo "kubectl port-forward svc/grafana -n monitoring 3000:80"

echo ""
echo "Port forward to specific pod for debugging:"
echo "kubectl port-forward pod/<pod-name> -n todo-app 8000:8000"
```

### 4. Comprehensive Debug Script
A complete script combining all debugging commands.

```bash
# scripts/comprehensive-debug.sh
#!/bin/bash

# Comprehensive Debug Script for Todo Chatbot Application

NAMESPACE="todo-app"
APP_LABEL="app=todo-chatbot"

echo "==========================================="
echo "Todo Chatbot Application Debugging Toolkit"
echo "==========================================="
echo ""

echo "1. Checking cluster status..."
kubectl cluster-info
echo ""

echo "2. Checking nodes..."
kubectl get nodes
echo ""

echo "3. Checking all namespaces..."
kubectl get namespaces
echo ""

echo "4. Checking pods in $NAMESPACE namespace..."
kubectl get pods -n $NAMESPACE
echo ""

echo "5. Checking services in $NAMESPACE namespace..."
kubectl get services -n $NAMESPACE
echo ""

echo "6. Checking deployments in $NAMESPACE namespace..."
kubectl get deployments -n $NAMESPACE
echo ""

echo "7. Checking Dapr sidecar status..."
kubectl get pods -n $NAMESPACE -o yaml | grep -A 5 -B 5 dapr
echo ""

echo "8. Checking Dapr components..."
kubectl get components.dapr.io -A
echo ""

echo "9. Checking Dapr subscriptions..."
kubectl get subscriptions.dapr.io -A
echo ""

echo "10. Checking Dapr control plane..."
kubectl get pods -n dapr-system
echo ""

echo "11. Getting events in $NAMESPACE namespace..."
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'
echo ""

echo "12. Select a pod to view detailed logs:"
kubectl get pods -n $NAMESPACE -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[*].ready

echo ""
read -p "Enter pod name to view logs: " SELECTED_POD

if [ ! -z "$SELECTED_POD" ]; then
    echo ""
    echo "=== Application Container Logs for $SELECTED_POD ==="
    kubectl logs $SELECTED_POD -n $NAMESPACE
    
    echo ""
    echo "=== Dapr Sidecar Logs for $SELECTED_POD ==="
    kubectl logs $SELECTED_POD -n $NAMESPACE -c daprd
    
    echo ""
    echo "=== Last 50 Lines of Combined Logs ==="
    kubectl logs $SELECTED_POD -n $NAMESPACE --all-containers=true --tail=50
    
    echo ""
    echo "=== Pod Description ==="
    kubectl describe pod $SELECTED_POD -n $NAMESPACE
fi

echo ""
echo "==========================================="
echo "Debugging Complete"
echo "==========================================="
```

### 5. Monitoring Setup Commands
Commands to set up monitoring for the application.

```bash
# scripts/monitoring-setup.sh
#!/bin/bash

echo "=== Monitoring Setup Commands ==="

echo "1. Deploy Prometheus and Grafana (if not already deployed):"
echo "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
echo "helm repo update"
echo "helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace"

echo ""
echo "2. Check if monitoring namespace exists:"
kubectl get ns monitoring || kubectl create namespace monitoring

echo ""
echo "3. Create ServiceMonitor for Dapr metrics:"
cat << EOF > dapr-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr-servicemonitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: todo-chatbot
  namespaceSelector:
    matchNames:
    - todo-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
EOF

echo "kubectl apply -f dapr-servicemonitor.yaml"

echo ""
echo "4. Create basic Prometheus configuration:"
cat << EOF > prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: \$1:\$2
        target_label: __address__
EOF

echo "kubectl apply -f prometheus-config.yaml"

echo ""
echo "5. Check if Dapr metrics are available:"
echo "kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080"
echo "Then visit http://localhost:8080 and check metrics"
```

### 6. Debug Commands Reference
A quick reference for common debugging commands.

```markdown
# debug-commands.md

# Debug Commands Reference

## Basic Pod Commands
- `kubectl get pods -n todo-app` - List all pods
- `kubectl describe pod <pod-name> -n todo-app` - Get pod details
- `kubectl logs <pod-name> -n todo-app` - View application logs
- `kubectl logs <pod-name> -n todo-app -c daprd` - View Dapr sidecar logs
- `kubectl logs <pod-name> -n todo-app --all-containers=true` - View all container logs

## Dapr-Specific Commands
- `kubectl get components.dapr.io -A` - List Dapr components
- `kubectl get subscriptions.dapr.io -A` - List Dapr subscriptions
- `dapr dashboard -k` - Launch Dapr dashboard
- `dapr status -k` - Check Dapr runtime status
- `kubectl logs -l app=todo-chatbot -n todo-app -c daprd` - View all Dapr sidecar logs

## Port Forwarding
- `kubectl port-forward svc/chat-api-service -n todo-app 8080:80` - Forward to Chat API
- `kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080` - Forward to Dapr dashboard
- `kubectl port-forward pod/<pod-name> -n todo-app 8000:8000` - Forward to specific pod

## Monitoring Commands
- `kubectl top pods -n todo-app` - Show pod resource usage
- `kubectl get hpa -n todo-app` - Check Horizontal Pod Autoscalers
- `kubectl get events -n todo-app --sort-by='.lastTimestamp'` - View recent events

## Troubleshooting Commands
- `kubectl exec -it <pod-name> -n todo-app -- /bin/sh` - Execute in pod
- `kubectl exec -it <pod-name> -n todo-app -c daprd -- /bin/sh` - Execute in Dapr sidecar
- `kubectl rollout status deployment/<deployment-name> -n todo-app` - Check deployment status
```

### 7. Dapr Dashboard Setup
Commands to launch and use the Dapr dashboard.

```bash
# scripts/dapr-dashboard.sh
#!/bin/bash

echo "=== Dapr Dashboard Setup ==="

echo "1. Launch Dapr dashboard:"
echo "dapr dashboard -k"
echo "This will open the dashboard at http://localhost:8080"

echo ""
echo "2. Alternative: Port forward to Dapr dashboard service:"
echo "kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080"

echo ""
echo "3. Once dashboard is running, you can:"
echo "   - View Dapr runtime status"
echo "   - Check component health"
echo "   - Monitor service-to-service calls"
echo "   - View pub/sub message flows"
echo "   - Inspect state stores"
echo "   - View configuration stores"

echo ""
echo "4. To stop the dashboard, press Ctrl+C in the terminal where it's running"
```

### 8. Metrics Collection Script
Script to collect and analyze metrics.

```bash
# scripts/metrics-collect.sh
#!/bin/bash

NAMESPACE="todo-app"

echo "=== Collecting Metrics ==="

echo "1. Resource usage by pods:"
kubectl top pods -n $NAMESPACE

echo ""
echo "2. Resource usage by nodes:"
kubectl top nodes

echo ""
echo "3. Deployment status:"
kubectl get deployments -n $NAMESPACE -o wide

echo ""
echo "4. Service status:"
kubectl get services -n $NAMESPACE

echo ""
echo "5. Horizontal Pod Autoscaler status:"
kubectl get hpa -n $NAMESPACE

echo ""
echo "6. Recent events:"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20

echo ""
echo "7. Dapr sidecar metrics (if Prometheus is configured):"
echo "Port forward to Prometheus and query: dapr_sidecar_uptime_seconds"

echo ""
echo "Metrics collection complete."
```

## Usage Instructions

### 1. Running the Debug Scripts
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run the comprehensive debug script
./scripts/comprehensive-debug.sh

# Or run specific scripts
./scripts/dapr-debug.sh
./scripts/port-forward.sh
```

### 2. Using the Debug Commands
```bash
# View logs for a specific pod
kubectl logs <pod-name> -n todo-app -c daprd

# Port forward to a service
kubectl port-forward svc/chat-api-service -n todo-app 8080:80

# Launch Dapr dashboard
dapr dashboard -k
```

### 3. Setting Up Monitoring
```bash
# Run the monitoring setup script
./scripts/monitoring-setup.sh

# Or manually apply the configuration
kubectl apply -f dapr-servicemonitor.yaml
```

## Common Debugging Scenarios

### 1. Application Not Responding
1. Check pod status: `kubectl get pods -n todo-app`
2. Check logs: `kubectl logs <pod-name> -n todo-app`
3. Check Dapr sidecar: `kubectl logs <pod-name> -n todo-app -c daprd`
4. Check service: `kubectl get svc chat-api-service -n todo-app`

### 2. Dapr Component Issues
1. Check components: `kubectl get components.dapr.io -A`
2. Check Dapr logs: `kubectl logs -l app=todo-chatbot -n todo-app -c daprd`
3. Check Dapr control plane: `kubectl get pods -n dapr-system`

### 3. Scaling Issues
1. Check HPA: `kubectl get hpa -n todo-app`
2. Check resource usage: `kubectl top pods -n todo-app`
3. Check deployment: `kubectl describe deployment/chat-api -n todo-app`

## Troubleshooting Tips

1. **Always check Dapr sidecar logs first** when facing integration issues
2. **Use `dapr dashboard -k`** for visual inspection of service interactions
3. **Verify component configurations** if pub/sub or state management isn't working
4. **Check resource limits** if pods are being evicted
5. **Review network policies** if services can't communicate