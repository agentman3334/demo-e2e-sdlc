# Spec: Frontend Kanban Board & Dashboard

## Feature
Kanban task board with drag-and-drop and dashboard with charts.

## Requirements
- FR-18: Kanban board (TaskBoardPage.jsx) — 3 columns, route: /projects/:id/board
- FR-19: Drag-and-drop between columns → auto-call status update API
- FR-20: Task create/edit modal
- FR-23: Dashboard (DashboardPage.jsx) — stats + progress + charts
- FR-24: Aggregated stats for all user projects
- FR-25-30: Role-based UI

## Library Choices
- DnD: @hello-pangea/dnd
- Charts: @ant-design/charts

## Jira Task
SCRUM-9