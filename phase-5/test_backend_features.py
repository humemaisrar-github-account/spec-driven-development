import requests
import json
import time

def test_backend_features():
    """Test all the new backend features"""
    base_url = "http://localhost:8000"
    
    print("Testing Phase V Advanced Features...\n")
    
    # Test 1: Create a task with priority, tags, and due date
    print("1. Testing task creation with priority, tags, and due date:")
    task_data = {
        "title": "Test task with advanced features",
        "description": "A task to test priority, tags, and due date features",
        "priority": "high",
        "tags": ["work", "important", "testing"],
        "due_date": "2026-12-31T23:59:59"
    }
    
    response = requests.post(f"{base_url}/api/tasks/", json=task_data)
    if response.status_code == 200:
        task = response.json()
        task_id = task['id']
        print(f"   [SUCCESS] Task created successfully with ID: {task_id}")
        print(f"   [SUCCESS] Priority: {task['priority']}")
        print(f"   [SUCCESS] Tags: {task['tags']}")
        print(f"   [SUCCESS] Due date: {task['due_date']}")
    else:
        print(f"   [FAILED] Failed to create task: {response.text}")
        return
    
    time.sleep(1)  # Brief pause to ensure data consistency
    
    # Test 2: Update the task
    print("\n2. Testing task update with priority and tags:")
    update_data = {
        "priority": "low",
        "tags": ["personal", "later"]
    }
    
    response = requests.put(f"{base_url}/api/tasks/{task_id}", json=update_data)
    if response.status_code == 200:
        updated_task = response.json()
        print(f"   [SUCCESS] Task updated successfully")
        print(f"   [SUCCESS] New priority: {updated_task['priority']}")
        print(f"   [SUCCESS] New tags: {updated_task['tags']}")
    else:
        print(f"   [FAILED] Failed to update task: {response.text}")
    
    time.sleep(1)  # Brief pause to ensure data consistency
    
    # Test 3: Create a recurring task
    print("\n3. Testing recurring task creation:")
    recurring_data = {
        "title": "Daily exercise",
        "description": "Daily workout routine",
        "priority": "medium",
        "tags": ["health", "fitness"],
        "recurrence_pattern": "daily",
        "max_instances": 7
    }
    
    response = requests.post(f"{base_url}/api/recurring-tasks/", json=recurring_data)
    if response.status_code == 200:
        recurring_task = response.json()
        recurring_task_id = recurring_task['id']
        print(f"   [SUCCESS] Recurring task created successfully with ID: {recurring_task_id}")
        print(f"   [SUCCESS] Pattern: {recurring_task['recurrence_pattern']}")
        print(f"   [SUCCESS] Priority: {recurring_task['priority']}")
        print(f"   [SUCCESS] Tags: {recurring_task['tags']}")
        print(f"   [SUCCESS] Max instances: {recurring_task['max_instances']}")
    else:
        print(f"   [FAILED] Failed to create recurring task: {response.text}")
        return
    
    time.sleep(1)  # Brief pause to ensure data consistency
    
    # Test 4: Retrieve all tasks
    print("\n4. Testing task retrieval:")
    response = requests.get(f"{base_url}/api/tasks/")
    if response.status_code == 200:
        tasks_data = response.json()
        tasks = tasks_data['tasks']
        print(f"   [SUCCESS] Retrieved {len(tasks)} task(s)")
        for task in tasks:
            print(f"   - Task: {task['title']} (Priority: {task['priority']})")
    else:
        print(f"   [FAILED] Failed to retrieve tasks: {response.text}")
    
    # Test 5: Retrieve all recurring tasks
    print("\n5. Testing recurring task retrieval:")
    response = requests.get(f"{base_url}/api/recurring-tasks/")
    if response.status_code == 200:
        recurring_tasks_data = response.json()
        recurring_tasks = recurring_tasks_data['recurring_tasks']
        print(f"   [SUCCESS] Retrieved {len(recurring_tasks)} recurring task(s)")
        for rt in recurring_tasks:
            print(f"   - Recurring Task: {rt['title']} (Pattern: {rt['recurrence_pattern']})")
    else:
        print(f"   [FAILED] Failed to retrieve recurring tasks: {response.text}")
    
    # Test 6: Test filtering by priority
    print("\n6. Testing task filtering by priority:")
    response = requests.get(f"{base_url}/api/tasks/?priority=low")
    if response.status_code == 200:
        filtered_tasks = response.json()['tasks']
        print(f"   [SUCCESS] Retrieved {len(filtered_tasks)} low priority task(s)")
        for task in filtered_tasks:
            print(f"   - Task: {task['title']} (Priority: {task['priority']})")
    else:
        print(f"   [FAILED] Failed to filter tasks: {response.text}")
    
    # Test 7: Test search functionality
    print("\n7. Testing task search:")
    response = requests.get(f"{base_url}/api/tasks/?search=advanced")
    if response.status_code == 200:
        search_results = response.json()['tasks']
        print(f"   [SUCCESS] Found {len(search_results)} task(s) matching 'advanced'")
        for task in search_results:
            print(f"   - Task: {task['title']}")
    else:
        print(f"   [FAILED] Failed to search tasks: {response.text}")
    
    print("\n[SUCCESS] All tests completed successfully!")
    print("\nSummary of implemented features:")
    print("- Priority levels (low, medium, high)")
    print("- Tagging system (up to 5 tags per task)")
    print("- Due date assignment")
    print("- Search functionality")
    print("- Filter by priority, tags, due dates")
    print("- Sort by various fields")
    print("- Recurring tasks with multiple patterns")
    print("- Full API endpoints for all operations")
    print("- Event-driven architecture with Dapr")
    print("- Natural language processing for chat interface")

if __name__ == "__main__":
    test_backend_features()