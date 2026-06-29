# Spec: Frontend Authentication Pages

## Feature
Login and register pages with auth context for the PMS frontend.

## Requirements
- FR-3: Login page (LoginPage.jsx) — email + password form, submit, error display
- FR-4: Register page (RegisterPage.jsx) — email + username + password + confirm password
- FR-5: Axios interceptor — auto-attach Authorization: Bearer <token>
- FR-6: Auto-redirect to /login on token expiry/invalid

## Routes
- /login — LoginPage
- /register — RegisterPage

## Auth Context
- AuthContext.jsx provides: user, token, login(), logout(), register(), isAuthenticated
- Token stored in localStorage
- 401 responses → clear token → redirect to /login

## Jira Task
SCRUM-4