# Spec: Backend Project CRUD & Team Member Management

## Feature
Project management API with CRUD operations and team member management.

## Requirements
- FR-7: Create project (POST /projects)
- FR-8: List projects (GET /projects) — paginated, filtered by user membership
- FR-9: Get project detail (GET /projects/{id}) — info + members + task stats
- FR-10: Update project (PUT /projects/{id})
- FR-11: Delete project (DELETE /projects/{id}) — soft delete
- FR-12: Add/remove members (POST/DELETE /projects/{id}/members)

## Models
- Project: id, name, description, owner_id, is_deleted, created_at, updated_at
- ProjectMember: id, project_id, user_id, role (owner/manager/member)

## Pagination Format
{ items: [...], total: N, page: N, size: N }

## Jira Task
SCRUM-6