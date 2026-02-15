---
name: kafka-topic-pubsub-configurator
description: Generate setup scripts and configurations for Kafka/Redpanda topics, Docker Compose setup, and Dapr pubsub integration. Create production-ready Kafka/Redpanda configurations with proper topic setup, authentication, and Dapr integration for event-driven architectures.
---

# Kafka Topic & PubSub Configurator

## Overview
Generate setup scripts and configurations for Kafka/Redpanda topics, Docker Compose setup, and Dapr pubsub integration for Phase 5 event-driven microservices applications.

## Core Components

### 1. Redpanda Local Docker Compose Setup
Single-node Redpanda setup for local development.

```yaml
# kafka-setup/redpanda-docker.yaml
version: '3.8'
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:v23.2.15
    command:
      - redpanda
      - start
      - --smp
      - '1'
      - --memory
      - 1G
      - --reserve-memory
      - 0M
      - --overprovisioned
      - --node-id
      - '0'
      - --check=false
    ports:
      - 9092:9092
      - 9644:9644
      - 29092:29092
    volumes:
      - redpanda_data:/var/lib/redpanda/data

  console:
    image: docker.redpanda.com/redpandadata/console:v2.2.3
    environment:
      CONFIG_FILEPATH: /tmp/console-config.yml
    command:
      - sh
      - -c
      - |
        echo '
        kafka:
          brokers: ["redpanda:29092"]
          schemaRegistry:
            enabled: true
            urls: ["http://redpanda:8081"]
        ' > /tmp/console-config.yml
        /app/console
    ports:
      - 8080:8080
    depends_on:
      - redpanda

volumes:
  redpanda_data:
```

### 2. Topic Creation Script
Script to create required Kafka topics with proper configuration.

```bash
# kafka-setup/create-topics.sh
#!/bin/bash

# Create Kafka topics for the Todo Chatbot application
echo "Creating Kafka topics..."

# Connect to Redpanda container and create topics
docker exec -t redpanda-1-redpanda-1 rpk topic create task-events --partitions 3 --replication-factor 1
docker exec -t redpanda-1-redpanda-1 rpk topic create reminders --partitions 3 --replication-factor 1
docker exec -t redpanda-1-redpanda-1 rpk topic create task-updates --partitions 3 --replication-factor 1

echo "Topics created successfully!"
echo "Available topics:"
docker exec -t redpanda-1-redpanda-1 rpk topic list
```

### 3. Redpanda Cloud Configuration Template
Template for Redpanda Cloud setup with authentication.

```yaml
# kafka-setup/redpanda-cloud-template.yaml
# Redpanda Cloud Configuration Template
# Replace placeholders with actual values from your Redpanda Cloud account

apiVersion: v1
kind: Secret
metadata:
  name: redpanda-cloud-credentials
  namespace: todo-app
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  bootstrap-servers: <base64-encoded-bootstrap-url>
```

### 4. Dapr pubsub.kafka Component for Redpanda Cloud
Dapr component configuration for Redpanda Cloud with SASL/SSL authentication.

```yaml
# kafka-setup/dapr-pubsub-redpanda-cloud.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-redpanda-cloud
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "your-cluster-id.redpanda.cloud:9092"  # Replace with your actual bootstrap URL
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: redpanda-cloud-credentials
      key: username
  - name: saslPassword
    secretKeyRef:
      name: redpanda-cloud-credentials
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-256"
  - name: consumerGroup
    value: "todo-app-consumer-group"
  - name: clientID
    value: "todo-app"
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "100ms"
  - name: disableTls
    value: "false"
auth:
  secretStore: kubernetes
```

### 5. Dapr pubsub.kafka Component for Local Redpanda
Dapr component configuration for local Redpanda development.

```yaml
# kafka-setup/dapr-pubsub-redpanda-local.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-redpanda-local
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-app-consumer-group"
  - name: clientID
    value: "todo-app"
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "100ms"
  - name: disableTls
    value: "true"
```

## Topic Configuration Details

### 1. task-events Topic
Used for task lifecycle events (created, updated, completed, deleted).

```bash
# kafka-setup/configure-task-events.sh
#!/bin/bash

# Create task-events topic with specific configuration
docker exec -t redpanda-1-redpanda-1 rpk topic create task-events \
  --partitions 3 \
  --replication-factor 1 \
  --config cleanup.policy=compact \
  --config retention.ms=604800000  # 7 days retention
```

### 2. reminders Topic
Used for scheduling and sending reminder notifications.

```bash
# kafka-setup/configure-reminders.sh
#!/bin/bash

# Create reminders topic with specific configuration
docker exec -t redpanda-1-redpanda-1 rpk topic create reminders \
  --partitions 3 \
  --replication-factor 1 \
  --config cleanup.policy=delete \
  --config retention.ms=86400000   # 1 day retention
```

### 3. task-updates Topic
Used for task status updates and synchronization.

```bash
# kafka-setup/configure-task-updates.sh
#!/bin/bash

# Create task-updates topic with specific configuration
docker exec -t redpanda-1-redpanda-1 rpk topic create task-updates \
  --partitions 3 \
  --replication-factor 1 \
  --config cleanup.policy=compact \
  --config retention.ms=259200000  # 3 days retention
```

## Test Scripts

### 1. Basic Publish Test
Simple script to test publishing messages to Kafka topics.

```python
# kafka-setup/test-publish.py
"""
Basic test script to publish messages to Kafka topics
Requires: pip install kafka-python
"""
from kafka import KafkaProducer
import json
import time

def test_publish():
    # Configure producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3
    )
    
    # Sample task event
    task_event = {
        "event_type": "task_created",
        "task_id": "task-123",
        "user_id": "user-456",
        "timestamp": int(time.time()),
        "data": {
            "title": "Sample Task",
            "due_date": "2023-12-31T23:59:59Z",
            "priority": "medium"
        }
    }
    
    # Publish to task-events topic
    producer.send('task-events', value=task_event)
    producer.flush()
    print("Published task event to task-events topic")
    
    # Sample reminder event
    reminder_event = {
        "task_id": "task-123",
        "title": "Sample Task",
        "due_at": "2023-12-31T23:59:59Z",
        "remind_at": "2023-12-31T23:49:59Z",
        "user_id": "user-456"
    }
    
    # Publish to reminders topic
    producer.send('reminders', value=reminder_event)
    producer.flush()
    print("Published reminder event to reminders topic")
    
    producer.close()

if __name__ == "__main__":
    test_publish()
```

### 2. Basic Consume Test
Simple script to test consuming messages from Kafka topics.

```python
# kafka-setup/test-consume.py
"""
Basic test script to consume messages from Kafka topics
Requires: pip install kafka-python
"""
from kafka import KafkaConsumer
import json

def test_consume(topic_name):
    # Configure consumer
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='test-consumer-group'
    )
    
    print(f"Listening to {topic_name}...")
    try:
        for message in consumer:
            print(f"Received message from {topic_name}:")
            print(f"Key: {message.key}")
            print(f"Value: {message.value}")
            print("---")
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test-consume.py <topic-name>")
        print("Example: python test-consume.py task-events")
    else:
        test_consume(sys.argv[1])
```

## Setup Instructions

### 1. Local Development Setup
```bash
# Start Redpanda locally
docker-compose -f kafka-setup/redpanda-docker.yaml up -d

# Wait for Redpanda to be ready
sleep 30

# Create topics
chmod +x kafka-setup/create-topics.sh
./kafka-setup/create-topics.sh

# Verify topics are created
docker exec -t redpanda-1-redpanda-1 rpk topic list
```

### 2. Apply Dapr Component
```bash
# For local development
kubectl apply -f kafka-setup/dapr-pubsub-redpanda-local.yaml

# For cloud deployment
kubectl apply -f kafka-setup/dapr-pubsub-redpanda-cloud.yaml
```

### 3. Test the Setup
```bash
# Install required packages
pip install kafka-python

# Test publishing
python kafka-setup/test-publish.py

# Test consuming (in another terminal)
python kafka-setup/test-consume.py task-events
```

## Production Considerations

### 1. Topic Configuration
- Adjust partition counts based on expected throughput
- Set appropriate retention policies
- Configure proper cleanup policies (compact vs delete)

### 2. Security
- Use SSL/TLS for all connections in production
- Implement proper authentication (SCRAM-SHA-256 for Redpanda Cloud)
- Store credentials securely using Kubernetes secrets

### 3. Monitoring
- Monitor topic lag and throughput
- Set up alerts for consumer group issues
- Track message delivery success rates

## Troubleshooting

### Common Issues:
1. **Connection refused**: Verify Redpanda is running and accessible
2. **Authentication failed**: Check credentials and authentication method
3. **Topic not found**: Ensure topics are created before applications start
4. **Consumer lag**: Check consumer performance and topic partitioning

### Useful Commands:
```bash
# Check Redpanda status
docker exec -t redpanda-1-redpanda-1 rpk cluster info

# List all topics
docker exec -t redpanda-1-redpanda-1 rpk topic list

# Describe a topic
docker exec -t redpanda-1-redpanda-1 rpk topic describe <topic-name>

# Check consumer groups
docker exec -t redpanda-1-redpanda-1 rpk group list
```

## Integration with Applications

To use these Kafka topics in your applications:

1. Reference the Dapr pubsub component in your application
2. Use Dapr's pub/sub APIs to publish and subscribe to events
3. Follow the defined event schemas for consistency

Example in Python:
```python
import dapr.clients

# Initialize Dapr client
dapr_client = dapr.clients.DaprClient()

# Publish an event
dapr_client.publish_event(
    pubsub_name='pubsub-redpanda-local',  # or 'pubsub-redpanda-cloud'
    topic_name='task-events',
    data=json.dumps(task_event),
    data_content_type='application/json'
)
```