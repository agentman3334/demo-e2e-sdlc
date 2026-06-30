"""
PMS E2E Test Server - Synchronous Flask version (avoids greenlet/async issues)
Implements the same API as the FastAPI backend using SQLite.
"""
import os
import uuid
import json
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_e2e.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            deadline TEXT,
            owner_id TEXT NOT NULL REFERENCES users(id),
            is_deleted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS project_members (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            user_id TEXT NOT NULL REFERENCES users(id),
            role TEXT DEFAULT 'member',
            joined_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            assignee_id TEXT REFERENCES users(id),
            due_date TEXT,
            is_deleted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()

def reset_db():
    conn = get_db()
    conn.executescript("""
        DROP TABLE IF EXISTS tasks;
        DROP TABLE IF EXISTS project_members;
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS users;
    """)
    conn.commit()
    conn.close()
    init_db()

# Initialize DB on startup
init_db()

# Auth helpers
import bcrypt
from jose import jwt

SECRET_KEY = "e2e-test-secret-key"
ALGORITHM = "HS256"

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"detail": "Not authenticated"}), 403)
    token = auth[7:]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None, (jsonify({"detail": "Invalid token type"}), 401)
        user_id = payload.get("sub")
    except Exception:
        return None, (jsonify({"detail": "Invalid or expired token"}), 401)
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,)).fetchone()
    conn.close()
    if not user:
        return None, (jsonify({"detail": "User not found or inactive"}), 401)
    return dict(user), None

def require_role(*roles):
    user, error = get_current_user()
    if error:
        return None, error
    if user["role"] not in roles:
        return None, (jsonify({"detail": "Insufficient permissions"}), 403)
    return user, None

def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    # Convert integer booleans
    for key in ['is_active', 'is_deleted']:
        if key in d:
            d[key] = bool(d[key])
    return d

# Create Flask app
app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# === HEALTH ===
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

# === TEST HELPERS ===
@app.route("/test/reset-db", methods=["POST"])
def test_reset():
    reset_db()
    return jsonify({"status": "reset"})

@app.route("/test/set-role", methods=["POST"])
def test_set_role():
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (data["role"], data["user_id"]))
    conn.commit()
    user = conn.execute("SELECT id, role FROM users WHERE id = ?", (data["user_id"],)).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"})
    return jsonify({"user_id": user["id"], "role": user["role"]})

# === AUTH ROUTES ===
@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")
        
        if not email or not password or not full_name:
            return jsonify({"detail": "Missing required fields"}), 422
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({"detail": "Invalid email format"}), 422
        
        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({"detail": "Email already registered"}), 400
        
        user_id = str(uuid.uuid4())
        hashed = hash_password(password)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, 'member', 1, ?, ?)",
            (user_id, email, hashed, full_name, now, now)
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(user)), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"detail": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"detail": "Missing required fields"}), 422
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if not user or not verify_password(password, user["hashed_password"]):
        return jsonify({"detail": "Invalid credentials"}), 401
    if not user["is_active"]:
        return jsonify({"detail": "Account is disabled"}), 403
    
    token_data = {"sub": user["id"], "role": user["role"]}
    return jsonify({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    })

@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return jsonify({"detail": "Invalid token type"}), 401
        user_id = payload.get("sub")
    except Exception:
        return jsonify({"detail": "Invalid or expired refresh token"}), 401
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({"detail": "User not found or inactive"}), 401
    
    token_data = {"sub": user["id"], "role": user["role"]}
    return jsonify({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    })

@app.route("/api/auth/me", methods=["GET"])
def get_me():
    user, error = get_current_user()
    if error:
        return error
    return jsonify(row_to_dict(user))

@app.route("/api/auth/me", methods=["PUT"])
def update_me():
    user, error = get_current_user()
    if error:
        return error
    
    data = request.get_json()
    conn = get_db()
    
    if "email" in data:
        existing = conn.execute("SELECT id FROM users WHERE email = ? AND id != ?", (data["email"], user["id"])).fetchone()
        if existing:
            conn.close()
            return jsonify({"detail": "Email already in use"}), 400
    
    updates = []
    values = []
    for field in ["full_name", "email"]:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])
    
    if updates:
        now = datetime.now(timezone.utc).isoformat()
        updates.append("updated_at = ?")
        values.append(now)
        values.append(user["id"])
        conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    
    updated = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    conn.close()
    return jsonify(row_to_dict(updated))

# === PROJECT ROUTES ===
@app.route("/api/projects/", methods=["GET"])
def list_projects():
    user, error = get_current_user()
    if error:
        return error
    
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    offset = (page - 1) * size
    
    conn = get_db()
    total = conn.execute(
        "SELECT COUNT(*) FROM projects p JOIN project_members pm ON pm.project_id = p.id WHERE pm.user_id = ? AND p.is_deleted = 0",
        (user["id"],)
    ).fetchone()[0]
    
    rows = conn.execute(
        "SELECT p.* FROM projects p JOIN project_members pm ON pm.project_id = p.id WHERE pm.user_id = ? AND p.is_deleted = 0 ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
        (user["id"], size, offset)
    ).fetchall()
    conn.close()
    
    return jsonify({
        "items": [row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "size": size
    })

@app.route("/api/projects/", methods=["POST"])
def create_project():
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    data = request.get_json()
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    conn = get_db()
    conn.execute(
        "INSERT INTO projects (id, name, description, status, deadline, owner_id, is_deleted, created_at, updated_at) VALUES (?, ?, ?, 'active', ?, ?, 0, ?, ?)",
        (project_id, data["name"], data.get("description"), data.get("deadline"), user["id"], now, now)
    )
    # Add creator as project_manager member
    member_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO project_members (id, project_id, user_id, role, joined_at) VALUES (?, ?, ?, 'project_manager', ?)",
        (member_id, project_id, user["id"], now)
    )
    conn.commit()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(project)), 201

@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    user, error = get_current_user()
    if error:
        return error
    
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    # Check membership
    member = conn.execute("SELECT id FROM project_members WHERE project_id = ? AND user_id = ?", (project_id, user["id"])).fetchone()
    conn.close()
    
    if not member and user["role"] != "admin":
        return jsonify({"detail": "Not a project member"}), 403
    
    return jsonify(row_to_dict(project))

@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    data = request.get_json()
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    updates = []
    values = []
    for field in ["name", "description", "status", "deadline"]:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])
    
    if updates:
        now = datetime.now(timezone.utc).isoformat()
        updates.append("updated_at = ?")
        values.append(now)
        values.append(project_id)
        conn.execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    
    updated = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(updated))

@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    user, error = require_role("admin")
    if error:
        return error
    
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE projects SET is_deleted = 1, updated_at = ? WHERE id = ?", (now, project_id))
    conn.commit()
    conn.close()
    return "", 204

@app.route("/api/projects/<project_id>/members", methods=["POST"])
def add_member(project_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    data = request.get_json()
    conn = get_db()
    
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    existing = conn.execute("SELECT id FROM project_members WHERE project_id = ? AND user_id = ?", (project_id, data["user_id"])).fetchone()
    if existing:
        conn.close()
        return jsonify({"detail": "User is already a member"}), 400
    
    target_user = conn.execute("SELECT * FROM users WHERE id = ?", (data["user_id"],)).fetchone()
    if not target_user:
        conn.close()
        return jsonify({"detail": "User not found"}), 404
    
    member_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    role = data.get("role", "member")
    conn.execute(
        "INSERT INTO project_members (id, project_id, user_id, role, joined_at) VALUES (?, ?, ?, ?, ?)",
        (member_id, project_id, data["user_id"], role, now)
    )
    conn.commit()
    member = conn.execute("SELECT * FROM project_members WHERE id = ?", (member_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(member)), 201

@app.route("/api/projects/<project_id>/members/<user_id>", methods=["DELETE"])
def remove_member(project_id, user_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    conn = get_db()
    member = conn.execute("SELECT * FROM project_members WHERE project_id = ? AND user_id = ?", (project_id, user_id)).fetchone()
    if not member:
        conn.close()
        return jsonify({"detail": "Member not found in project"}), 404
    
    conn.execute("DELETE FROM project_members WHERE project_id = ? AND user_id = ?", (project_id, user_id))
    conn.commit()
    conn.close()
    return "", 204

# === TASK ROUTES ===
@app.route("/api/tasks/", methods=["GET"])
def list_tasks():
    user, error = get_current_user()
    if error:
        return error
    
    project_id = request.args.get("project_id")
    status_filter = request.args.get("status")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    offset = (page - 1) * size
    
    conn = get_db()
    query = "SELECT * FROM tasks WHERE is_deleted = 0"
    count_query = "SELECT COUNT(*) FROM tasks WHERE is_deleted = 0"
    params = []
    
    if project_id:
        query += " AND project_id = ?"
        count_query += " AND project_id = ?"
        params.append(project_id)
    if status_filter:
        query += " AND status = ?"
        count_query += " AND status = ?"
        params.append(status_filter)
    
    total = conn.execute(count_query, params).fetchone()[0]
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    rows = conn.execute(query, params + [size, offset]).fetchall()
    conn.close()
    
    return jsonify({
        "items": [row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "size": size
    })

@app.route("/api/tasks/projects/<project_id>/tasks", methods=["POST"])
def create_task(project_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    data = request.get_json()
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    conn.execute(
        "INSERT INTO tasks (id, project_id, title, description, status, priority, assignee_id, due_date, is_deleted, created_at, updated_at) VALUES (?, ?, ?, ?, 'todo', ?, ?, ?, 0, ?, ?)",
        (task_id, project_id, data["title"], data.get("description"), data.get("priority", "medium"), data.get("assignee_id"), data.get("due_date"), now, now)
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(task)), 201

@app.route("/api/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    user, error = get_current_user()
    if error:
        return error
    
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND is_deleted = 0", (task_id,)).fetchone()
    conn.close()
    
    if not task:
        return jsonify({"detail": "Task not found"}), 404
    return jsonify(row_to_dict(task))

@app.route("/api/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    data = request.get_json()
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND is_deleted = 0", (task_id,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"detail": "Task not found"}), 404
    
    if user["role"] == "member" and task["assignee_id"] != user["id"]:
        conn.close()
        return jsonify({"detail": "Can only update your own tasks"}), 403
    
    updates = []
    values = []
    for field in ["title", "description", "status", "priority", "assignee_id", "due_date"]:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])
    
    if updates:
        now = datetime.now(timezone.utc).isoformat()
        updates.append("updated_at = ?")
        values.append(now)
        values.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(updated))

@app.route("/api/tasks/<task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    user, error = get_current_user()
    if error:
        return error
    
    data = request.get_json()
    new_status = data.get("status")
    valid_statuses = ["todo", "in_progress", "in_review", "done"]
    if new_status not in valid_statuses:
        return jsonify({"detail": f"Invalid status. Must be one of: {valid_statuses}"}), 400
    
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND is_deleted = 0", (task_id,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"detail": "Task not found"}), 404
    
    if user["role"] == "member" and task["assignee_id"] != user["id"]:
        conn.close()
        return jsonify({"detail": "Can only update your own tasks"}), 403
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (new_status, now, task_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(updated))

@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    user, error = require_role("admin", "project_manager")
    if error:
        return error
    
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND is_deleted = 0", (task_id,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"detail": "Task not found"}), 404
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE tasks SET is_deleted = 1, updated_at = ? WHERE id = ?", (now, task_id))
    conn.commit()
    conn.close()
    return "", 204

# === ANALYTICS ROUTES ===
@app.route("/api/analytics/dashboard", methods=["GET"])
def dashboard_stats():
    user, error = get_current_user()
    if error:
        return error
    
    conn = get_db()
    # Get user's project IDs
    project_rows = conn.execute(
        "SELECT project_id FROM project_members WHERE user_id = ?", (user["id"],)
    ).fetchall()
    project_ids = [r["project_id"] for r in project_rows]
    
    if not project_ids:
        conn.close()
        return jsonify({"total_tasks": 0, "completed": 0, "in_progress": 0, "overdue": 0, "projects": []})
    
    placeholders = ",".join(["?"] * len(project_ids))
    total = conn.execute(f"SELECT COUNT(*) FROM tasks WHERE project_id IN ({placeholders}) AND is_deleted = 0", project_ids).fetchone()[0]
    completed = conn.execute(f"SELECT COUNT(*) FROM tasks WHERE project_id IN ({placeholders}) AND status = 'done' AND is_deleted = 0", project_ids).fetchone()[0]
    in_progress = conn.execute(f"SELECT COUNT(*) FROM tasks WHERE project_id IN ({placeholders}) AND status = 'in_progress' AND is_deleted = 0", project_ids).fetchone()[0]
    overdue = conn.execute(f"SELECT COUNT(*) FROM tasks WHERE project_id IN ({placeholders}) AND status != 'done' AND is_deleted = 0 AND due_date < datetime('now')", project_ids).fetchone()[0]
    
    projects = []
    for pid in project_ids:
        p = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (pid,)).fetchone()
        if not p:
            continue
        p_total = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND is_deleted = 0", (pid,)).fetchone()[0]
        p_done = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'done' AND is_deleted = 0", (pid,)).fetchone()[0]
        progress = round((p_done / p_total) * 100) if p_total > 0 else 0
        projects.append({"id": p["id"], "name": p["name"], "status": p["status"], "progress": progress})
    
    conn.close()
    return jsonify({"total_tasks": total, "completed": completed, "in_progress": in_progress, "overdue": overdue, "projects": projects})

@app.route("/api/analytics/project/<project_id>", methods=["GET"])
def project_stats(project_id):
    user, error = get_current_user()
    if error:
        return error
    
    conn = get_db()
    member = conn.execute("SELECT id FROM project_members WHERE project_id = ? AND user_id = ?", (project_id, user["id"])).fetchone()
    if not member and user["role"] != "admin":
        conn.close()
        return jsonify({"detail": "Not a project member"}), 403
    
    project = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not project:
        conn.close()
        return jsonify({"detail": "Project not found"}), 404
    
    total = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND is_deleted = 0", (project_id,)).fetchone()[0]
    
    status_counts = {}
    for s in ["todo", "in_progress", "in_review", "done"]:
        count = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = ? AND is_deleted = 0", (project_id, s)).fetchone()[0]
        status_counts[s] = count
    
    priority_counts = {}
    for p in ["low", "medium", "high", "critical"]:
        count = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND priority = ? AND is_deleted = 0", (project_id, p)).fetchone()[0]
        priority_counts[p] = count
    
    overdue = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status != 'done' AND is_deleted = 0 AND due_date < datetime('now')", (project_id,)).fetchone()[0]
    progress = round((status_counts.get("done", 0) / total) * 100) if total > 0 else 0
    
    conn.close()
    return jsonify({
        "project_id": project_id,
        "project_name": project["name"],
        "total_tasks": total,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "overdue": overdue,
        "progress": progress
    })


if __name__ == "__main__":
    print("Starting PMS E2E Test Server on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)