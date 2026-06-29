# Design: Backend Authentication System (JWT)

## Architecture
FastAPI router + service layer + SQLAlchemy async model + Pydantic schemas.

## Files
- `backend/app/routers/auth.py` — /auth/register, /auth/login, /auth/me endpoints
- `backend/app/services/auth_service.py` — password hashing (passlib/bcrypt), JWT generation (python-jose), user lookup
- `backend/app/schemas/auth.py` — RegisterRequest, LoginRequest, TokenResponse, UserResponse
- `backend/app/models/user.py` — User SQLAlchemy model with role enum
- `backend/app/utils/security.py` — get_current_user Depends(), create_access_token(), verify_password()

## JWT Config
- Algorithm: HS256
- Secret: from config.SECRET_KEY
- Expiry: 30 minutes
- Payload: { "sub": user_id, "role": user.role }

## Auth Flow
1. Register: validate unique email/username → hash password → insert User → return 201
2. Login: lookup by email → verify password → create JWT → return token
3. Protected routes: Depends(get_current_user) extracts Bearer token → decode JWT → fetch user → inject into handler

## Error Handling
- 409 Conflict: duplicate email or username
- 401 Unauthorized: invalid credentials or expired token
- 422 Validation Error: missing/invalid request fields