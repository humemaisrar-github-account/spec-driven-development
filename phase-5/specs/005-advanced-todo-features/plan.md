# Implementation Plan: Phase V Part A – Intermediate & Advanced Features

**Branch**: `005-advanced-todo-features` | **Date**: 2026-02-15 | **Spec**: [../005-advanced-todo-features/spec.md](../005-advanced-todo-features/spec.md)
**Input**: Feature specification from `/specs/005-advanced-todo-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extending the Phase IV Todo Chatbot with advanced features (priorities, tags, search/filter/sort, recurring tasks, due dates & reminders) using an event-driven architecture with Dapr. The implementation will enhance the existing FastAPI backend with new microservices for handling recurring tasks and reminders, while maintaining the conversational chat interface. All new features will be built as loosely coupled extensions that communicate asynchronously via Kafka events through Dapr Pub/Sub.

## Technical Context

**Language/Version**: Python 3.11 (aligns with existing FastAPI backend)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK, Pydantic, kafka-python (for Dapr abstraction), asyncpg
**Storage**: Neon PostgreSQL via Dapr State Management (aligns with constitution)
**Testing**: pytest with integration and unit tests for new features
**Target Platform**: Kubernetes (Minikube local → cloud deployment)
**Project Type**: Web application (existing backend + new microservices)
**Performance Goals**: <500ms task operations, ±30s reminder accuracy (from constitution)
**Constraints**: Event-driven architecture, Dapr abstraction layer, <500ms CRUD latency (from constitution)
**Scale/Scope**: Support 1000+ tasks per user, 1000+ events/min throughput (from constitution)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Compliance Verification:**
- ✅ Event-Driven First – Loose Coupling: All new features will use Dapr Pub/Sub for communication
- ✅ Dapr as the Runtime Abstraction Layer: All infrastructure interactions via Dapr sidecars
- ✅ Scalable & Production-Grade Microservices: Breaking features into independent services
- ✅ Security & Portability by Design: Secrets via Dapr, YAML-driven config
- ✅ Performance, Reliability & Observability: Async Python, <500ms ops, ±30s reminder accuracy
- ✅ Development Discipline: Following agentic workflow, linking to task IDs

**Technology Stack Compliance:**
- ✅ Backend: FastAPI + SQLModel (Phase IV base) - COMPLIANT
- ✅ Database: Neon PostgreSQL (via Dapr State) - COMPLIANT
- ✅ Messaging: Kafka-compatible (Redpanda) - COMPLIANT
- ✅ Runtime: Dapr (full building blocks) - COMPLIANT
- ✅ Orchestration: Kubernetes - COMPLIANT

**Explicit Prohibitions Check:**
- ❌ Polling loops for reminders/recurring: Will use Dapr Jobs API instead - COMPLIANT
- ❌ Direct Kafka client libraries in app code: Will use Dapr Pub/Sub abstraction - COMPLIANT
- ❌ Hardcoded URLs, connection strings, or secrets: Will use Dapr Secrets - COMPLIANT
- ❌ Monolithic blocking operations: Using async Python - COMPLIANT
- ❌ Vendor lock-in: Using Dapr abstraction - COMPLIANT

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-todo-features/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Enhanced task model with priority, tags, due_date, etc.
│   │   └── recurring_task.py # Recurring task model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py  # Task operations with new features
│   │   ├── recurring_service.py # Recurring task logic
│   │   └── reminder_service.py # Reminder scheduling
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # Main API router
│   │   ├── tasks.py         # Task endpoints with search/filter/sort
│   │   └── recurring_tasks.py # Recurring task endpoints
│   ├── dapr_components/
│   │   ├── pubsub.yaml      # Kafka/Redpanda pub/sub configuration
│   │   ├── statestore.yaml  # PostgreSQL state store configuration
│   │   └── secrets.yaml     # Secret store configuration
│   └── events/
│       ├── __init__.py
│       ├── handlers.py      # Event handlers for recurring tasks and reminders
│       └── schemas.py       # Pydantic schemas for event payloads
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
        └── task_events_contract.py # Contract tests for task events

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# New microservices for advanced features
recurring-task-service/
├── src/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── dapr_components/
└── tests/

notification-service/
├── src/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── dapr_components/
└── tests/
```

**Structure Decision**: Web application with additional microservices for advanced features. The existing backend is enhanced with new models and services, while recurring tasks and notifications are handled by dedicated microservices to maintain loose coupling as required by the constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple microservices | Constitution requires scalable & production-grade microservices | Single monolith would violate constitution principle of scalable microservices |
