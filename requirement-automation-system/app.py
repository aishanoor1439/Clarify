from flask import Flask, request, jsonify, render_template, session
import re
import json
import os
import mysql.connector
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = "replace_with_strong_secret_key"

bcrypt = Bcrypt(app)

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="requirement_automation"
)

# JSON file for optional requirement analysis storage
DATA_FILE = "requirements.json"

# ---------------------------
# DECORATORS
# ---------------------------
def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "user":
            return jsonify({"error": "User login required"}), 401
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            return jsonify({"error": "Admin access only"}), 401
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    """Allows both admin and user to access"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return wrapper

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def save_requirement_json(result):
    """Optional: store analysis in JSON"""
    data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    data.append(result)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def classify_requirement(tokens):
    functional_keywords = ['login', 'upload', 'download', 'generate', 'search', 'create', 'send', 'delete']
    non_functional_keywords = ['fast', 'secure', 'scalable', 'reliable', 'user-friendly', 'efficient']
    t_lower = [t.lower() for t in tokens]
    if any(word in t_lower for word in functional_keywords):
        return "Functional"
    elif any(word in t_lower for word in non_functional_keywords):
        return "Non-Functional"
    return "Uncertain"

# ---------------------------
# AUTH ROUTES
# ---------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                (email, hashed_pw, role)
            )
            db.commit()
        return jsonify({"message": "Registered successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid password"}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    redirect_url = "/dashboard" if user["role"] == "admin" else "/ui"
    return jsonify({"message": "Login successful", "redirect": redirect_url})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

# ---------------------------
# UI ROUTES
# ---------------------------
@app.route('/ui')
@user_required
def ui():
    return render_template('projects.html')

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/data')
@admin_required
def dashboard_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []
    return jsonify(data)

# ---------------------------
# PROJECT MANAGEMENT
# ---------------------------
@app.route('/project/create', methods=['POST'])
@user_required
def create_project():
    data = request.get_json()
    project_name = data.get("project_name")
    user_id = session.get("user_id")

    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO projects (user_id, project_name) VALUES (%s, %s)",
                (user_id, project_name)
            )
            db.commit()
        return jsonify({"message": "Project created successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/projects', methods=['GET'])
@user_required
def get_projects():
    user_id = session.get("user_id")
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, project_name FROM projects WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
    projects = [{"id": r["id"], "name": r["project_name"]} for r in rows]
    return jsonify(projects)

# ---------------------------
# REQUIREMENTS MANAGEMENT
# ---------------------------
@app.route('/project/<int:project_id>/add_requirement', methods=['POST'])
@user_required
def add_requirement(project_id):
    data = request.get_json()
    requirement_text = data.get("requirement")
    if not requirement_text:
        return jsonify({"error": "Requirement text is missing"}), 400

    tokens = re.findall(r'\b\w+\b', requirement_text)
    stop_words = set(['the','is','at','which','on','a','an','and','or','to','in','for','of','by','with','should'])
    filtered_tokens = [w for w in tokens if w.lower() not in stop_words]
    category = classify_requirement(filtered_tokens)

    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO requirements (project_id, requirement_text, category) VALUES (%s, %s, %s)",
                (project_id, requirement_text, category)
            )
            db.commit()
        result = {
            "original": requirement_text,
            "tokens": tokens,
            "filtered_tokens": filtered_tokens,
            "category": category
        }
        save_requirement_json(result)
        return jsonify(result), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/project/<int:project_id>/requirements', methods=['GET'])
@user_required
def get_project_requirements(project_id):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT id, requirement_text AS text, category, created_at FROM requirements WHERE project_id=%s ORDER BY created_at DESC",
            (project_id,)
        )
        rows = cursor.fetchall()
    return jsonify(rows)

# ---------------------------
# ADMIN ROUTES
# ---------------------------
@app.route('/admin/projects')
@admin_required
def admin_projects():
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT p.id, p.project_name, u.email AS user_email FROM projects p JOIN users u ON p.user_id=u.id"
        )
        rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/admin/project/<int:project_id>')
@admin_required
def admin_project_requirements(project_id):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM requirements WHERE project_id=%s", (project_id,))
        rows = cursor.fetchall()
    return jsonify(rows)

# ---------------------------
# MESSAGING
# ---------------------------
@app.route('/messages/<int:project_id>', methods=['GET'])
@user_required
def get_user_messages(project_id):
    user_id = session["user_id"]
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.content, m.parent_id, m.created_at, u.email AS sender_email
            FROM messages m
            JOIN users u ON m.sender_id=u.id
            WHERE (m.sender_id=%s OR m.receiver_id=%s) AND m.project_id=%s
            ORDER BY m.created_at ASC
        """, (user_id, user_id, project_id))
        rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    project_id = data.get("project_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")
    parent_id = data.get("parent_id")  # optional

    if not receiver_id or not content:
        return jsonify({"error": "Missing receiver_id or content"}), 400

    sender_id = session["user_id"]
    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO messages (project_id, sender_id, receiver_id, content, parent_id) VALUES (%s,%s,%s,%s,%s)",
                (project_id, sender_id, receiver_id, content, parent_id)
            )
            db.commit()
        return jsonify({"message": "Message sent successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/get_admin')
@user_required
def get_admin():
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, email FROM users WHERE role='admin' LIMIT 1")
        admin = cursor.fetchone()
    return jsonify(admin)

# ---------------------------
# ROOT
# ---------------------------
@app.route('/')
def home():
    return "Requirement Automation System is Running!"

# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
