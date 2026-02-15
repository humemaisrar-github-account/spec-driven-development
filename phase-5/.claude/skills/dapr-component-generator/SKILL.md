---
name: dapr-component-generator
description: Generate Dapr component YAML files for pubsub, state management, bindings, and secret stores. Create production-ready Dapr component configurations with proper security practices and integration with external services like Kafka/Redpanda, PostgreSQL/Neon, and Kubernetes secrets.
---

# Dapr Component Generator

## Overview
Generate Dapr component YAML files for Phase 5 microservices applications. This skill creates production-ready Dapr component configurations with proper security practices and integration with external services.

## Core Components

### 1. pubsub.kafka Component
Configure Kafka/Redpanda for event-driven communication between services.

```yaml
# dapr-components/pubsub-kafka.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"  # Or your Redpanda broker address
  - name: consumerGroup
    value: "todo-app-consumer-group"
  - name: clientID
    value: "todo-app"
  - name: authRequired
    value: "false"  # Set to "true" if authentication is required
  - name: saslUsername
    secretKeyRef:
      name: redpanda-username
      key: username
  - name: saslPassword
    secretKeyRef:
      name: redpanda-password
      key: password
  - name: saslMechanism
    value: "PLAIN"
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "100ms"
auth:
  secretStore: kubernetes
```

### 2. state.postgresql Component
Configure PostgreSQL/Neon for state persistence.

```yaml
# dapr-components/state-postgresql.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: state-postgresql
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: neon-db-connection
      key: connectionString
  - name: actorStateStore
    value: "true"
  - name: concurrency
    value: "last-write"
  - name: isolationLevel
    value: "snapshot"
auth:
  secretStore: kubernetes
```

### 3. bindings.cron Component (Scheduled Reminders Fallback)
Configure cron bindings for scheduled tasks (prefer Dapr Jobs API for exact timing).

```yaml
# dapr-components/bindings-cron.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-binding
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "*/5 * * * *"  # Every 5 minutes (adjust as needed)
```

### 4. secretstores.kubernetes Component
Configure Kubernetes secret store for secure credential management.

```yaml
# dapr-components/secretstore-kubernetes.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

## Secret Management Setup

### Create Kubernetes Secrets for Sensitive Data

```yaml
# dapr-components/secrets/neon-db-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: neon-db-connection
  namespace: todo-app
type: Opaque
data:
  connectionString: <base64-encoded-connection-string>
  # Example: "host=ep-xxx.neon.tech user=xxx password=xxx dbname=xxx sslmode=require"
```

```yaml
# dapr-components/secrets/redpanda-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: redpanda-credentials
  namespace: todo-app
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
```

## Additional Components

### 5. jobs.api Component (Preferred for Scheduled Reminders)
Configure Dapr Jobs API for exact-time scheduling (preferred over cron bindings).

```yaml
# dapr-components/jobs-api.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: jobs-api
spec:
  type: jobs.api
  version: v1
  metadata:
  - name: enabled
    value: "true"
  - name: schedulerAddress
    value: "dapr-scheduler:50005"
```

### 6. configuration Component (Optional)
Configure configuration store if needed for dynamic configuration.

```yaml
# dapr-components/configuration.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: app-config
spec:
  type: configuration.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-password
      key: password
auth:
  secretStore: kubernetes
```

### 7. lock Component (Optional)
Configure distributed locking if needed for concurrent operations.

```yaml
# dapr-components/lock.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: app-lock
spec:
  type: lock.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-password
      key: password
auth:
  secretStore: kubernetes
```

## Deployment Instructions

### 1. Apply Dapr Components
```bash
# Apply all Dapr components
kubectl apply -f dapr-components/
```

### 2. Verify Components
```bash
# Check if components are applied correctly
kubectl get components.dapr.io -A
```

### 3. Check Dapr Sidecar Logs
```bash
# Verify that Dapr sidecars can connect to components
kubectl logs <pod-name> daprd
```

## Security Best Practices

### 1. Secret Management
- Always use `secretKeyRef` for sensitive data
- Never hardcode credentials in component files
- Store secrets in Kubernetes secrets or external secret stores

### 2. Connection String Format for Neon
```
host=ep-xxx.neon.tech user=xxx password=xxx dbname=xxx sslmode=require
```

### 3. Authentication
- Enable authentication for all external services
- Use TLS encryption for all connections
- Regularly rotate credentials

## Troubleshooting

### Common Issues:
1. **Connection refused**: Verify broker/service addresses are correct
2. **Authentication failed**: Check credentials and permissions
3. **Component not found**: Ensure component names match in application code
4. **Secret not accessible**: Verify secret store configuration and permissions

### Debug Commands:
```bash
# Check Dapr sidecar status
kubectl exec <pod-name> -- daprd status

# Get detailed component info
kubectl describe component <component-name>
```

## Integration with Applications

To use these components in your applications, reference them by name in your Dapr annotations or configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "my-app"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: app
        image: my-app:latest
```

Then in your application code, you can use the components by their names:
- Pub/Sub: Use `pubsub-kafka` for publishing/subscribing
- State: Use `state-postgresql` for state management
- Secrets: Access secrets via the `kubernetes` secret store