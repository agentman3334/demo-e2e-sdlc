# Spec: Backend Task CRUD & Analytics

## Feature
Task management API with CRUD, status updates, and analytics.

## Requirements
- FR-15: Create task (POST /tasks)
- FR-16: Update status (PATCH /tasks/{id}/status)
- FR-16b: General update (PATCH /tasks/{id}) — title, description, assignee, priority
- FR-16c: Delete task (DELETE /tasks/{id}) — soft delete
- FR-17: List tasks (GET /tasks) — filter by project_id, sort by status/priority
- FR-21: Analytics (GET /analytics/project/{id}) — task stats
- FR-22: Progress (GET /analytics/progress) — completion % per project

## Data Definitions
- Priority: low / medium / high (default: medium)
- Status: todo / in_progress / done (any transition for MVP)

## Task Model
id, title, description, project_id, assignee_id, status, priority, is_deleted, created_at, updated_at

## Jira Task
SCRUM-8