# Spec: CI/CD Pipeline & Docker Configuration

## Feature
GitHub Actions 3-stage workflow, Docker configuration, deployment setup.

## Requirements
- FR-31: GitHub Actions workflow: Build → SonarCloud → JFrog Upload
- FR-32: Build stage: vite build + python lint/test
- FR-33: SonarCloud stage: upload analysis, Quality Gate
- FR-34: JFrog stage: upload artifacts, Xray scan
- FR-35: Manual trigger (workflow_dispatch)
- FR-36: Docker Compose: frontend + backend + postgres
- FR-37: Frontend Dockerfile: multi-stage (build → nginx)
- FR-38: Backend Dockerfile: Python 3.11 slim

## Secrets Required
- SONAR_TOKEN, SONAR_PROJECT_KEY, SONAR_ORGANIZATION
- JFROG_URL, JFROG_USER, JFROG_TOKEN

## Jira Task
SCRUM-10