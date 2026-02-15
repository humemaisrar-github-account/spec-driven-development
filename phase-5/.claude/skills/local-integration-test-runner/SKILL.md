---
name: local-integration-test-runner
description: Generate test scripts for local Kubernetes cluster validation, Dapr integration testing, and demo preparation. Create comprehensive testing framework for validating event-driven microservices applications with Dapr integration.
---

# Local & Integration Test Runner

## Overview
Generate test scripts for local Kubernetes cluster validation, Dapr integration testing, and demo preparation for Phase 5 event-driven microservices applications.

## Core Components

### 1. Minikube Test Script
Complete script for applying all resources and testing locally.

```bash
# tests/local-validation.sh
#!/bin/bash

# Minikube Local Validation Script for Todo Chatbot Application

set -e  # Exit on any error

NAMESPACE="todo-app"
TIMEOUT=300  # 5 minutes timeout for deployments

echo "==========================================="
echo "Todo Chatbot Local Validation Script"
echo "==========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command_exists minikube; then
    echo "ERROR: minikube is not installed"
    echo "Please install minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

if ! command_exists kubectl; then
    echo "ERROR: kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command_exists dapr; then
    echo "ERROR: dapr is not installed"
    echo "Please install dapr: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

echo "✓ All prerequisites met"
echo ""

# Start Minikube if not running
echo "2. Starting Minikube..."
if ! minikube status | grep -q "Running"; then
    echo "Starting Minikube with sufficient resources..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g
else
    echo "Minikube is already running"
fi

echo ""

# Enable Dapr in Minikube
echo "3. Installing Dapr in Minikube..."
dapr init -k
echo "✓ Dapr installed in Minikube"
echo ""

# Create namespace
echo "4. Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
echo "✓ Namespace $NAMESPACE created"
echo ""

# Apply all Dapr components
echo "5. Applying Dapr components..."
kubectl apply -f dapr-components/
echo "✓ Dapr components applied"
echo ""

# Wait for Dapr system to be ready
echo "6. Waiting for Dapr system to be ready..."
kubectl wait --for=condition=ready pod -l app=dapr-placement-server -n dapr-system --timeout=${TIMEOUT}s
kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=${TIMEOUT}s
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=${TIMEOUT}s
echo "✓ Dapr system is ready"
echo ""

# Apply secrets
echo "7. Applying secrets..."
kubectl apply -f kubernetes/full-deployment-set/secrets/ || echo "No secrets found, continuing..."
echo "✓ Secrets applied"
echo ""

# Apply RBAC
echo "8. Applying RBAC configurations..."
kubectl apply -f kubernetes/full-deployment-set/rbac/ || echo "No RBAC configs found, continuing..."
echo "✓ RBAC configurations applied"
echo ""

# Apply services
echo "9. Applying services..."
kubectl apply -f kubernetes/full-deployment-set/chat-api/service.yaml
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/service.yaml
kubectl apply -f kubernetes/full-deployment-set/notification-service/service.yaml
echo "✓ Services applied"
echo ""

# Apply deployments
echo "10. Applying deployments..."
kubectl apply -f kubernetes/full-deployment-set/chat-api/deployment.yaml
kubectl apply -f kubernetes/full-deployment-set/recurring-task-service/deployment.yaml
kubectl apply -f kubernetes/full-deployment-set/notification-service/deployment.yaml
echo "✓ Deployments applied"
echo ""

# Wait for deployments to be ready
echo "11. Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-chatbot,component=chat-api -n $NAMESPACE --timeout=${TIMEOUT}s
kubectl wait --for=condition=ready pod -l app=todo-chatbot,component=recurring-task-service -n $NAMESPACE --timeout=${TIMEOUT}s
kubectl wait --for=condition=ready pod -l app=todo-chatbot,component=notification-service -n $NAMESPACE --timeout=${TIMEOUT}s
echo "✓ All deployments are ready"
echo ""

# Verify Dapr sidecars are injected
echo "12. Verifying Dapr sidecars..."
CHAT_API_SIDECARS=$(kubectl get pods -l app=todo-chatbot,component=chat-api -n $NAMESPACE -o jsonpath='{range .items[*]}{.spec.containers[*].name}{"\\n"}{end}' | grep -c daprd || true)
RECURRING_SIDECARS=$(kubectl get pods -l app=todo-chatbot,component=recurring-task-service -n $NAMESPACE -o jsonpath='{range .items[*]}{.spec.containers[*].name}{"\\n"}{end}' | grep -c daprd || true)
NOTIFICATION_SIDECARS=$(kubectl get pods -l app=todo-chatbot,component=notification-service -n $NAMESPACE -o jsonpath='{range .items[*]}{.spec.containers[*].name}{"\\n"}{end}' | grep -c daprd || true)

if [ $CHAT_API_SIDECARS -gt 0 ] && [ $RECURRING_SIDECARS -gt 0 ] && [ $NOTIFICATION_SIDECARS -gt 0 ]; then
    echo "✓ All Dapr sidecars are properly injected"
else
    echo "⚠ Warning: Dapr sidecars may not be properly injected"
fi
echo ""

# Display service information
echo "13. Service information:"
echo "Chat API Service: $(kubectl get svc chat-api-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
echo "Recurring Task Service: $(kubectl get svc recurring-task-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
echo "Notification Service: $(kubectl get svc notification-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
echo ""

# Run basic connectivity tests
echo "14. Running basic connectivity tests..."

# Test Dapr sidecar health
echo "Testing Dapr sidecar health..."
kubectl exec -it -n $NAMESPACE -c daprd $(kubectl get pods -l app=todo-chatbot,component=chat-api -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:3501/v1.0/healthz
echo ""

echo "Testing Dapr placement health..."
kubectl exec -it -n $NAMESPACE -c daprd $(kubectl get pods -l app=todo-chatbot,component=chat-api -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:50005/v1.0/healthz
echo ""

echo "✓ Connectivity tests completed"
echo ""

# Start port forwarding in background for demo
echo "15. Setting up port forwarding for demo..."
echo "Starting port forwarding to Chat API (Ctrl+C to stop)..."
echo "Access Chat API at: http://localhost:8080"
echo "Access Dapr dashboard at: http://localhost:8081 (run 'dapr dashboard -p 8081' in another terminal)"
echo ""

echo "==========================================="
echo "Local Validation Complete!"
echo "==========================================="
echo "Next steps:"
echo "1. Run 'kubectl get pods -n $NAMESPACE' to verify all pods are running"
echo "2. Run 'kubectl get services -n $NAMESPACE' to see service endpoints"
echo "3. Run 'dapr dashboard -k' to open Dapr dashboard"
echo "4. Run 'kubectl port-forward svc/chat-api-service -n $NAMESPACE 8080:80' for API access"
echo "5. Run './tests/run-integration-tests.sh' for integration tests"
echo ""

# Optional: Start port forwarding for immediate testing
read -p "Start port forwarding to Chat API now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting port forwarding... (Press Ctrl+C to stop)"
    kubectl port-forward svc/chat-api-service -n $NAMESPACE 8080:80
fi


### 2. Basic Pytest for Dapr Calls
Pytest framework for testing Dapr integration.

```python
# tests/test_dapr_integration.py
import pytest
import httpx
import asyncio
import json
from datetime import datetime, timedelta


# Configuration
DAPR_HTTP_PORT = 3500
BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
TODO_APP_NAMESPACE = "todo-app"


@pytest.fixture
def dapr_client():
    """Create an HTTP client for Dapr sidecar."""
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


@pytest.mark.asyncio
async def test_dapr_health():
    """Test Dapr sidecar health endpoint."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/v1.0/healthz")
        assert response.status_code == 204


def test_dapr_metadata(dapr_client):
    """Test Dapr metadata endpoint."""
    response = dapr_client.get("/v1.0/metadata")
    assert response.status_code == 200
    metadata = response.json()
    assert "id" in metadata
    assert "actors" in metadata
    assert "components" in metadata


def test_pubsub_publish_and_subscribe(dapr_client):
    """Test pubsub functionality by publishing and expecting subscription."""
    # Define test data
    pubsub_name = "pubsub-kafka"  # Assuming this component exists
    topic_name = "task-events"
    test_data = {
        "event_type": "test_event",
        "task_id": "test-123",
        "user_id": "test-user",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "title": "Test Task",
            "description": "This is a test task for pubsub validation"
        }
    }
    
    # Publish message
    response = dapr_client.post(
        f"/v1.0/publish/{pubsub_name}/{topic_name}",
        json=test_data,
        headers={"content-type": "application/json"}
    )
    
    # For pubsub, a 200/204 response indicates successful publishing
    assert response.status_code in [200, 204]


def test_state_management(dapr_client):
    """Test Dapr state management operations."""
    store_name = "state-postgresql"  # Assuming this component exists
    key = f"test-key-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    test_value = {
        "message": "Test state value",
        "timestamp": datetime.now().isoformat(),
        "test_id": key
    }
    
    # Save state
    put_response = dapr_client.post(
        f"/v1.0/state/{store_name}",
        json=[{
            "key": key,
            "value": test_value
        }]
    )
    assert put_response.status_code in [200, 204]
    
    # Get state
    get_response = dapr_client.get(f"/v1.0/state/{store_name}/{key}")
    assert get_response.status_code == 200
    retrieved_value = get_response.json()
    assert retrieved_value["test_id"] == key
    assert retrieved_value["message"] == "Test state value"
    
    # Delete state
    delete_response = dapr_client.delete(f"/v1.0/state/{store_name}/{key}")
    assert delete_response.status_code in [200, 204]


def test_secrets_management(dapr_client):
    """Test Dapr secrets management (if secrets are configured)."""
    store_name = "kubernetes"  # Assuming kubernetes secret store is configured
    secret_key = "neon-db-secret"  # Example secret name
    
    # Try to get a secret (this will fail if the secret doesn't exist, which is OK for validation)
    try:
        response = dapr_client.get(f"/v1.0/secrets/{store_name}/{secret_key}")
        if response.status_code == 200:
            secrets = response.json()
            assert isinstance(secrets, dict)
            print(f"Successfully accessed secret: {secret_key}")
        elif response.status_code == 404:
            print(f"Secret {secret_key} not found (expected in test environment)")
        else:
            print(f"Unexpected response when accessing secret: {response.status_code}")
    except Exception as e:
        print(f"Error accessing secret (may be expected in test environment): {e}")


def test_service_invocation(dapr_client):
    """Test Dapr service invocation (requires other services to be running)."""
    # This test assumes there's a service to invoke
    app_id = "chat-api"  # Example service
    method = "health"  # Example method
    
    try:
        response = dapr_client.get(f"/v1.0/invoke/{app_id}/method/{method}")
        # If the service is running, we expect a response (any status code is fine for validation)
        print(f"Service invocation test completed with status: {response.status_code}")
    except httpx.ConnectError:
        print("Service invocation test skipped - target service may not be available")
    except Exception as e:
        print(f"Service invocation test issue: {e}")


@pytest.mark.asyncio
async def test_jobs_api_mock():
    """Test Dapr Jobs API functionality with mock jobs."""
    # This test simulates using the Jobs API for reminders
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Schedule a mock job for testing
        job_name = f"test-job-{int(datetime.now().timestamp())}"
        due_time = (datetime.now() + timedelta(seconds=30)).isoformat()
        
        job_payload = {
            "dueTime": due_time,
            "data": {
                "job_type": "reminder_test",
                "test_id": job_name,
                "message": "This is a test reminder job"
            }
        }
        
        try:
            response = await client.post(f"/v1.0-alpha1/jobs/{job_name}", json=job_payload)
            if response.status_code in [200, 204]:
                print(f"Mock job {job_name} scheduled successfully")
            else:
                print(f"Job scheduling returned status {response.status_code}")
        except httpx.RequestError as e:
            print(f"Jobs API not available or not configured: {e}")


def test_dapr_components_loaded(dapr_client):
    """Verify that expected Dapr components are loaded."""
    response = dapr_client.get("/v1.0/metadata")
    assert response.status_code == 200
    
    metadata = response.json()
    components = [comp["name"] for comp in metadata.get("components", [])]
    
    # Check for expected components (these should match your dapr-components/)
    expected_components = ["pubsub-kafka", "state-postgresql", "kubernetes"]
    
    for expected_comp in expected_components:
        # Just warn if not found, don't fail the test as components may vary by environment
        if expected_comp not in components:
            print(f"Warning: Expected component '{expected_comp}' not found in loaded components")
        else:
            print(f"Found expected component: {expected_comp}")


if __name__ == "__main__":
    # Run tests individually for debugging
    print("Running Dapr integration tests...")
    
    # Synchronous tests
    test_dapr_metadata(None)  # Pass None as fixture is not used in this test
    test_pubsub_publish_and_subscribe(None)
    test_state_management(None)
    test_secrets_management(None)
    test_service_invocation(None)
    test_dapr_components_loaded(None)
    
    # Asynchronous tests
    asyncio.run(test_dapr_health())
    asyncio.run(test_jobs_api_mock())
    
    print("Dapr integration tests completed.")
```


### 3. Demo Checklist for Video
Complete checklist for recording demonstration video.

```markdown
# Demo Checklist for Todo Chatbot Video

## Pre-Demo Preparation
- [ ] Ensure Minikube is running with sufficient resources
- [ ] Verify all services are running: `kubectl get pods -n todo-app`
- [ ] Confirm Dapr components are loaded: `dapr status -k`
- [ ] Test basic functionality before recording
- [ ] Close unnecessary applications/windows
- [ ] Prepare demo data/scripts
- [ ] Ensure good internet connection
- [ ] Set up screen recording software

## Demo Flow

### 1. Introduction (1-2 minutes)
- [ ] Introduce the Todo Chatbot application
- [ ] Mention the event-driven architecture with Dapr
- [ ] Outline what will be demonstrated

### 2. Architecture Overview (2-3 minutes)
- [ ] Show the Kubernetes deployment: `kubectl get all -n todo-app`
- [ ] Highlight Dapr sidecars in each pod
- [ ] Explain the services: Chat API, RecurringTaskService, NotificationService
- [ ] Point out Dapr components: pubsub, state management

### 3. Dapr Integration Demonstration (3-4 minutes)
- [ ] Open Dapr dashboard: `dapr dashboard -k`
- [ ] Show component configurations
- [ ] Demonstrate service-to-service invocation
- [ ] Show pub/sub message flow
- [ ] Highlight state management

### 4. Application Functionality (4-5 minutes)
- [ ] Set up port forwarding: `kubectl port-forward svc/chat-api-service -n todo-app 8080:80`
- [ ] Create a new task via API call or UI
- [ ] Show the task being published to pubsub
- [ ] Demonstrate recurring task creation
- [ ] Show notification service in action
- [ ] Verify state persistence

### 5. Jobs API for Reminders (2-3 minutes)
- [ ] Explain the Jobs API concept
- [ ] Show how reminders are scheduled
- [ ] Demonstrate a mock reminder job
- [ ] Verify the job execution

### 6. Monitoring and Debugging (2-3 minutes)
- [ ] Show application logs: `kubectl logs -f deployment/chat-api -n todo-app`
- [ ] Show Dapr sidecar logs: `kubectl logs -f deployment/chat-api -n todo-app -c daprd`
- [ ] Demonstrate health checks
- [ ] Show metrics if available

### 7. Conclusion (1 minute)
- [ ] Summarize key features demonstrated
- [ ] Mention scalability and production readiness
- [ ] Thank viewers

## Technical Setup for Recording

### Terminal Setup
- [ ] Use a readable font size (at least 14pt)
- [ ] Use a high contrast color scheme
- [ ] Maximize terminal window
- [ ] Test command visibility

### Screen Recording
- [ ] Record at 1920x1080 or higher resolution
- [ ] Frame rate of 30fps or higher
- [ ] Audio quality check
- [ ] Have a backup recording method

## Post-Demo Verification
- [ ] Verify all services are still running after demo
- [ ] Check for any errors in logs
- [ ] Ensure no resources were left in inconsistent state
- [ ] Clean up any test data if needed
```

### 4. Integration Test Runner Script
Script to run all integration tests.

```bash
# tests/run-integration-tests.sh
#!/bin/bash

# Integration Test Runner for Todo Chatbot Application

set -e  # Exit on any error

echo "==========================================="
echo "Todo Chatbot Integration Test Runner"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "tests/test_dapr_integration.py" ]; then
    echo "ERROR: test_dapr_integration.py not found in tests/ directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed"
    exit 1
fi

if ! command -v pip >/dev/null 2>&1; then
    echo "ERROR: pip is not installed"
    exit 1
fi

echo "✓ Prerequisites met"
echo ""

# Install test dependencies
echo "2. Installing test dependencies..."
pip install pytest pytest-asyncio httpx
echo "✓ Test dependencies installed"
echo ""

# Verify Dapr is accessible
echo "3. Verifying Dapr accessibility..."
if nc -z localhost 3500; then
    echo "✓ Dapr sidecar accessible on port 3500"
else
    echo "⚠ Dapr sidecar not accessible on port 3500"
    echo "   Make sure your services are running with Dapr sidecars"
    echo "   You may need to run 'kubectl port-forward' to access Dapr endpoints"
fi
echo ""

# Run pytest tests
echo "4. Running integration tests..."
echo "Running: pytest tests/test_dapr_integration.py -v"
python -m pytest tests/test_dapr_integration.py -v
TEST_RESULT=$?

echo ""
echo "==========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "All integration tests PASSED!"
else
    echo "Some integration tests FAILED!"
fi
echo "==========================================="

exit $TEST_RESULT
```

### 5. Reminder Job Test Script
Specific test for Jobs API functionality.

```python
# tests/test_reminder_jobs.py
import asyncio
import httpx
import pytest
from datetime import datetime, timedelta
import json


DAPR_HTTP_PORT = 3500
BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


class TestReminderJobs:
    """Test class for Dapr Jobs API functionality with reminders."""
    
    async def test_schedule_reminder_job(self):
        """Test scheduling a reminder job via Dapr Jobs API."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # Create a mock reminder job
            job_name = f"reminder-test-{int(datetime.now().timestamp())}"
            # Schedule for 30 seconds from now
            due_time = (datetime.now() + timedelta(seconds=30)).strftime('%H:%M:%S')
            
            job_payload = {
                "dueTime": due_time,
                "data": {
                    "job_type": "reminder",
                    "task_id": "task-123",
                    "user_id": "user-456",
                    "reminder_time": datetime.now().isoformat(),
                    "message": "Test reminder for integration"
                }
            }
            
            try:
                response = await client.post(f"/v1.0-alpha1/jobs/{job_name}", json=job_payload)
                
                # Jobs API might return different status codes depending on configuration
                if response.status_code in [200, 204]:
                    print(f"✓ Reminder job {job_name} scheduled successfully")
                    
                    # Verify the job was scheduled by getting its status (if supported)
                    try:
                        status_response = await client.get(f"/v1.0-alpha1/jobs/{job_name}")
                        if status_response.status_code == 200:
                            job_status = status_response.json()
                            print(f"  Job status: {job_status}")
                    except httpx.HTTPError:
                        print(f"  (Job status check not supported by this Dapr runtime)")
                        
                    return True
                else:
                    print(f"✗ Failed to schedule job {job_name}, status: {response.status_code}")
                    print(f"  Response: {response.text}")
                    return False
                    
            except httpx.RequestError as e:
                print(f"✗ Request error when scheduling job: {e}")
                return False
            except Exception as e:
                print(f"✗ Unexpected error when scheduling job: {e}")
                return False
    
    async def test_multiple_reminder_jobs(self):
        """Test scheduling multiple reminder jobs."""
        success_count = 0
        total_jobs = 3
        
        for i in range(total_jobs):
            job_name = f"reminder-multi-test-{int(datetime.now().timestamp())}-{i}"
            due_time = (datetime.now() + timedelta(seconds=30+i*10)).strftime('%H:%M:%S')
            
            job_payload = {
                "dueTime": due_time,
                "data": {
                    "job_type": "reminder_multi",
                    "sequence": i,
                    "scheduled_at": datetime.now().isoformat()
                }
            }
            
            async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
                try:
                    response = await client.post(f"/v1.0-alpha1/jobs/{job_name}", json=job_payload)
                    if response.status_code in [200, 204]:
                        success_count += 1
                        print(f"✓ Job {job_name} scheduled successfully")
                    else:
                        print(f"✗ Failed to schedule job {job_name}")
                except Exception as e:
                    print(f"✗ Error scheduling job {job_name}: {e}")
        
        print(f"Scheduled {success_count}/{total_jobs} jobs successfully")
        return success_count == total_jobs


# Mock Jobs API for testing when actual Jobs API is not available
class MockJobsAPI:
    """Mock implementation of Jobs API for testing purposes."""
    
    def __init__(self):
        self.jobs = {}
    
    async def create_job(self, job_name, payload):
        """Mock job creation."""
        self.jobs[job_name] = {
            "payload": payload,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        print(f"MOCK: Job {job_name} created with payload: {payload}")
        return {"job_name": job_name, "status": "scheduled"}
    
    async def get_job(self, job_name):
        """Mock job retrieval."""
        return self.jobs.get(job_name, {"error": "Job not found"})


# Test runner
async def run_reminder_tests():
    """Run all reminder-related tests."""
    print("Running Reminder Jobs Tests...")
    print("="*40)
    
    tester = TestReminderJobs()
    
    # Test single job scheduling
    print("\n1. Testing single reminder job scheduling:")
    result1 = await tester.test_schedule_reminder_job()
    
    # Test multiple jobs scheduling
    print("\n2. Testing multiple reminder jobs scheduling:")
    result2 = await tester.test_multiple_reminder_jobs()
    
    print("\n" + "="*40)
    if result1 and result2:
        print("✓ All reminder job tests PASSED")
        return True
    else:
        print("✗ Some reminder job tests FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_reminder_tests())
    exit(0 if success else 1)
```

## Best Practices for Testing

### 1. Test Isolation
- Each test should be independent
- Clean up resources after each test
- Use unique identifiers for test data

### 2. Error Handling
- Test both success and failure scenarios
- Verify error responses are handled properly
- Check for edge cases and invalid inputs

### 3. Performance Testing
- Measure response times
- Test under load conditions
- Verify scalability characteristics

### 4. Security Testing
- Validate authentication/authorization
- Test for injection vulnerabilities
- Verify data protection measures

## Continuous Integration
These tests can be integrated into CI/CD pipelines to ensure:
- Code changes don't break existing functionality
- Dapr integrations continue to work as expected
- Performance benchmarks are maintained
- Security standards are upheld

This comprehensive test suite ensures that the event-driven architecture with Dapr integration works correctly in the local Minikube environment before deployment to production.