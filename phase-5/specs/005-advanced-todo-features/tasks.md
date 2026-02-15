---

description: "Task list for Phase V Part A - Intermediate & Advanced Features"
---

# Tasks: Phase V Part A – Intermediate & Advanced Features

**Input**: Design documents from `/specs/005-advanced-todo-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in backend/
- [X] T002 [P] Initialize Python project with FastAPI, SQLModel, Dapr SDK dependencies in backend/
- [X] T003 [P] Set up Dapr components directory with pubsub.yaml, statestore.yaml, secrets.yaml in backend/dapr_components/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Set up enhanced Task model with priority, tags, due_date in backend/src/models/task.py
- [X] T005 [P] Create RecurringTask model in backend/src/models/recurring_task.py
- [X] T006 [P] Define TaskPriority and TaskStatus enums in backend/src/models/__init__.py
- [X] T007 [P] Define RecurrencePattern enum in backend/src/models/__init__.py
- [X] T008 Create TaskEvent schema in backend/src/events/schemas.py
- [X] T009 [P] Create TaskEventType enum in backend/src/events/schemas.py
- [X] T010 Set up database migrations for new fields and tables
- [X] T011 Create base TaskService in backend/src/services/task_service.py
- [X] T012 [P] Create RecurringTaskService in backend/src/services/recurring_service.py
- [X] T013 [P] Create ReminderService in backend/src/services/reminder_service.py
- [X] T014 Set up event handlers module in backend/src/events/handlers.py
- [X] T015 Configure Dapr Pub/Sub component for Kafka/Redpanda in backend/dapr_components/pubsub.yaml
- [X] T016 Configure Dapr State Store component for PostgreSQL in backend/dapr_components/statestore.yaml
- [X] T017 Configure Dapr Secrets component in backend/dapr_components/secrets.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Priority & Tag Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (low, medium, high) to tasks and add tags (max 5 per task)

**Independent Test**: Users can create tasks with priority and tags, and modify them later

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Contract test for POST /tasks with priority and tags in tests/contract/test_task_creation.py
- [ ] T019 [P] [US1] Contract test for PUT /tasks/{task_id} with priority and tags in tests/contract/test_task_update.py
- [ ] T020 [P] [US1] Integration test for priority and tag validation in tests/integration/test_task_validation.py

### Implementation for User Story 1

- [X] T021 [P] [US1] Update Task model with priority and tags fields in backend/src/models/task.py
- [X] T022 [P] [US1] Update TaskService to handle priority and tags in backend/src/services/task_service.py
- [X] T023 [US1] Implement POST /tasks endpoint with priority and tags in backend/src/api/tasks.py
- [X] T024 [US1] Implement PUT /tasks/{task_id} endpoint with priority and tags in backend/src/api/tasks.py
- [X] T025 [US1] Add validation for max 5 tags per task in backend/src/services/task_service.py
- [X] T026 [US1] Add default medium priority when none specified in backend/src/services/task_service.py
- [X] T027 [US1] Add logging for priority and tag operations in backend/src/services/task_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Search, Filter & Sort (Priority: P2)

**Goal**: Enable users to search, filter and sort tasks by priority, tags, due dates, and other criteria

**Independent Test**: Users can search for tasks by text, filter by priority/tags/due dates, and sort by various fields

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T028 [P] [US2] Contract test for GET /tasks with search, filter, sort parameters in tests/contract/test_task_search.py
- [ ] T029 [P] [US2] Integration test for full-text search functionality in tests/integration/test_search.py

### Implementation for User Story 2

- [X] T030 [P] [US2] Update TaskService with search, filter, sort methods in backend/src/services/task_service.py
- [X] T031 [US2] Implement GET /tasks endpoint with search, filter, sort capabilities in backend/src/api/tasks.py
- [X] T032 [US2] Add full-text search indexes to Task model in backend/src/models/task.py
- [X] T033 [US2] Add filtering by priority, tags, due dates in backend/src/services/task_service.py
- [X] T034 [US2] Add sorting by due date, priority, created_at, title in backend/src/services/task_service.py
- [X] T035 [US2] Add pagination support to GET /tasks endpoint in backend/src/api/tasks.py
- [X] T036 [US2] Add validation for search and filter parameters in backend/src/services/task_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Due Dates & Reminders (Priority: P3)

**Goal**: Enable users to set due dates for tasks and receive configurable reminders

**Independent Test**: Users can set due dates and receive reminders at configurable offsets

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T037 [P] [US3] Contract test for POST /tasks with due_date in tests/contract/test_task_due_dates.py
- [ ] T038 [P] [US3] Contract test for reminder scheduling in tests/contract/test_reminders.py
- [ ] T039 [P] [US3] Integration test for reminder delivery timing in tests/integration/test_reminder_timing.py

### Implementation for User Story 3

- [X] T040 [P] [US3] Update Task model with due_date field in backend/src/models/task.py
- [X] T041 [US3] Update TaskService to handle due dates in backend/src/services/task_service.py
- [X] T042 [US3] Implement PUT /tasks/{task_id} with due_date updates in backend/src/api/tasks.py
- [X] T043 [US3] Create ReminderService for scheduling and managing reminders in backend/src/services/reminder_service.py
- [ ] T044 [US3] Implement Dapr Jobs API integration for exact-time reminders in backend/src/services/reminder_service.py
- [X] T045 [US3] Create event handler for TASK_REMINDER_SCHEDULED in backend/src/events/handlers.py
- [X] T046 [US3] Add reminder offset configuration (5 min, 1 hour, 1 day) in backend/src/services/reminder_service.py
- [X] T047 [US3] Add overdue task indicators in backend/src/services/task_service.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Recurring Tasks (Priority: P4)

**Goal**: Enable users to create recurring tasks with various patterns (daily, weekly, monthly, custom)

**Independent Test**: Users can create recurring tasks that automatically generate new instances

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [ ] T048 [P] [US4] Contract test for POST /recurring-tasks endpoint in tests/contract/test_recurring_tasks.py
- [ ] T049 [P] [US4] Integration test for recurring task instance creation in tests/integration/test_recurring_instances.py
- [ ] T050 [P] [US4] Contract test for recurring task completion triggering next instance in tests/contract/test_recurring_completion.py

### Implementation for User Story 4

- [X] T051 [P] [US4] Complete RecurringTask model implementation in backend/src/models/recurring_task.py
- [X] T052 [US4] Implement RecurringTaskService with pattern logic in backend/src/services/recurring_service.py
- [X] T053 [US4] Create POST /recurring-tasks endpoint in backend/src/api/recurring_tasks.py
- [X] T054 [US4] Create GET /recurring-tasks endpoint in backend/src/api/recurring_tasks.py
- [X] T055 [US4] Create PUT /recurring-tasks/{id} endpoint in backend/src/api/recurring_tasks.py
- [X] T056 [US4] Create DELETE /recurring-tasks/{id} endpoint in backend/src/api/recurring_tasks.py
- [X] T057 [US4] Implement recurring task instance creation logic in backend/src/services/recurring_service.py
- [X] T058 [US4] Add max 10 future instances constraint in backend/src/services/recurring_service.py
- [X] T059 [US4] Create event handler for recurring task completion in backend/src/events/handlers.py
- [X] T060 [US4] Add event publishing for recurring task events in backend/src/events/handlers.py

**Checkpoint**: At this point, all user stories should be independently functional

---

## Phase 7: User Story 5 - Chat Interface Integration (Priority: P5)

**Goal**: Integrate all advanced features into the existing conversational chat interface

**Independent Test**: Users can use natural language to set priorities, tags, due dates, recurring tasks via chat

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

- [ ] T061 [P] [US5] Integration test for natural language processing of priority commands in tests/integration/test_nlp_priority.py
- [ ] T062 [P] [US5] Integration test for natural language processing of tag commands in tests/integration/test_nlp_tags.py
- [ ] T063 [P] [US5] Integration test for natural language processing of due date commands in tests/integration/test_nlp_due_dates.py

### Implementation for User Story 5

- [X] T064 [P] [US5] Update chat command parser to recognize priority settings in backend/src/chat_parser.py
- [X] T065 [US5] Update chat command parser to recognize tag additions in backend/src/chat_parser.py
- [X] T066 [US5] Update chat command parser to recognize due date settings in backend/src/chat_parser.py
- [X] T067 [US5] Update chat command parser to recognize recurring task creation in backend/src/chat_parser.py
- [X] T068 [US5] Add natural language processing for search/filter/sort commands in backend/src/chat_parser.py
- [X] T069 [US5] Integrate reminder notifications into chat interface in backend/src/services/reminder_service.py
- [X] T070 [US5] Add chat responses for all new features in backend/src/chat_responses.py

**Checkpoint**: All features now integrated into the conversational interface

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T071 [P] Documentation updates in docs/
- [ ] T072 Code cleanup and refactoring
- [ ] T073 Performance optimization across all stories
- [ ] T074 [P] Additional unit tests (if requested) in tests/unit/
- [ ] T075 Security hardening
- [ ] T076 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 (requires priority/tag functionality)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Integrates all previous stories into chat interface

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /tasks with priority and tags in tests/contract/test_task_creation.py"
Task: "Contract test for PUT /tasks/{task_id} with priority and tags in tests/contract/test_task_update.py"
Task: "Integration test for priority and tag validation in tests/integration/test_task_validation.py"

# Launch all models for User Story 1 together:
Task: "Update Task model with priority and tags fields in backend/src/models/task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Priority & Tag Management)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence