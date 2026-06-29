# Spec: Backend Authentication System (JWT)

## Feature
User registration and login with JWT-based authentication for the PMS backend.

## Requirements
- FR-1: User registration endpoint (POST /auth/register) — email, username, password (bcrypt)
- FR-2: User login endpoint (POST /auth/login) — validate credentials, return JWT (30min expiry)
- FR-6: Token validation middleware (FastAPI Depends) for protected routes

## User Model
- id: UUID
- email: String (unique, indexed)
- username: String (unique, indexed)
- hashed_password: String
- role: Enum (admin, pm, member) — default: member
- created_at: DateTime

## API Contract
- POST /auth/register → 201 { id, email, username, role } | 409 duplicate
- POST /auth/login → 200 { access_token, token_type: "bearer" } | 401 invalid
- GET /auth/me → 200 { id, email, username, role } | 401 unauthenticated

## Jira Task
SCRUM-5