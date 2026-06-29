# Spec: Frontend Project Pages

## Feature
Project list and detail pages for the PMS frontend.

## Requirements
- FR-13: Projects list page (ProjectsPage.jsx) — project cards, create modal
- FR-14: Project detail page (ProjectDetailPage.jsx) — info + members + tasks

## API Contract (from SCRUM-6)
- GET /projects → { items: [{ id, name, description, owner, memberCount, taskStats }], total, page, size }
- GET /projects/{id} → { id, name, description, owner, members: [...], taskStats: {...} }

## Jira Task
SCRUM-7