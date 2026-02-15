# Quickstart Guide: Phase V Part A – Intermediate & Advanced Features

## Overview
This guide explains how to set up and run the enhanced Todo Chatbot with advanced features (priorities, tags, search/filter/sort, recurring tasks, due dates & reminders).

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Minikube (for local Kubernetes)
- Dapr CLI installed
- Node.js 18+ (for frontend, if applicable)

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd hackathon-02/phase-5
```

### 2. Install Backend Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Dapr
```bash
# Initialize Dapr (if not already done)
dapr init

# Verify Dapr is running
dapr status -k
```

### 4. Configure Environment
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
DAPR_COMPONENTS_PATH=./dapr_components
```

### 5. Set Up Database
```bash
# Run database migrations
cd backend
alembic upgrade head
```

### 6. Start Services

#### Option A: Local Development (without Kubernetes)
```bash
# Terminal 1: Start Dapr with the application
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --components-path ./dapr_components python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start the recurring task service
cd recurring-task-service
dapr run --app-id recurring-task-service --app-port 8001 --dapr-http-port 3501 --components-path ./dapr_components python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: Start the notification service
cd notification-service
dapr run --app-id notification-service --app-port 8002 --dapr-http-port 3502 --components-path ./dapr_components python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

#### Option B: Kubernetes with Minikube
```bash
# Start Minikube
minikube start

# Install Dapr in Kubernetes
dapr init -k

# Deploy Kafka/Redpanda and PostgreSQL to Minikube
kubectl apply -f deployments/kafka-redpanda.yaml
kubectl apply -f deployments/postgresql.yaml

# Wait for deployments to be ready
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s

# Deploy the services
kubectl apply -f deployments/todo-backend.yaml
kubectl apply -f deployments/recurring-task-service.yaml
kubectl apply -f deployments/notification-service.yaml

# Verify deployments
kubectl get pods
kubectl get services
```

## Using Advanced Features

### Setting Task Priority
```
User: "Add grocery shopping with high priority"
System: "Added task 'grocery shopping' with high priority"
```

### Adding Tags to Tasks
```
User: "Create task 'Prepare presentation' #work #urgent"
System: "Added task 'Prepare presentation' with tags: work, urgent"
```

### Setting Due Dates and Reminders
```
User: "Schedule meeting with client tomorrow at 3pm, remind me 1 hour before"
System: "Scheduled task 'meeting with client' for tomorrow at 3pm with reminder at 2pm"
```

### Creating Recurring Tasks
```
User: "Remind me to take medication every day at 8am"
System: "Created recurring task: take medication daily at 8am"
```

### Searching and Filtering Tasks
```
User: "Show me all #work tasks due this week"
System: "Displaying 3 tasks with #work tag due this week..."

User: "Find tasks about 'presentation'"
System: "Found 2 tasks mentioning 'presentation': ..."
```

### Sorting Tasks
```
User: "Sort my tasks by due date"
System: "Tasks sorted by due date..."
```

## Testing the Features

### Unit Tests
```bash
cd backend
python -m pytest tests/unit/
```

### Integration Tests
```bash
cd backend
python -m pytest tests/integration/
```

### Contract Tests
```bash
cd backend
python -m pytest tests/contract/
```

## Troubleshooting

### Common Issues
1. **Dapr Sidecar Not Found**: Ensure Dapr is initialized (`dapr init`)
2. **Database Connection Issues**: Verify PostgreSQL is running and credentials are correct
3. **Kafka Connection Issues**: Ensure Kafka/Redpanda is running and accessible

### Checking Service Status
```bash
# Check Dapr sidecars
dapr status -k

# Check Kubernetes resources
kubectl get pods
kubectl get services
kubectl get deployments

# View logs
kubectl logs <pod-name>
```

## Next Steps
- Explore the API documentation at `/docs` endpoint
- Customize Dapr components for your specific infrastructure
- Scale services based on your load requirements
- Monitor services using Dapr's built-in metrics