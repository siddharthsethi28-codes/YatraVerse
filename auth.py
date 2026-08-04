from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db import get_db_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

# ─────────────────────────────────────────
#   POST /api/auth/register
#   Register a new traveler (from popup form)
# ─────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name', '').strip()
    email      = data.get('email', '').strip().lower()
    phone      = data.get('phone', '').strip()
    city       = data.get('city', '').strip()
    interest   = data.get('interest', '').strip()

    # Validation
    if not first_name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    if '@' not in email:
        return jsonify({'error': 'Invalid email address'}), 400

    cur = get_db_connection()

    # Check if email already registered
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    existing = cur.fetchone()
    if existing:
        return jsonify({'error': 'Email already registered. Please login.'}), 409

    # Insert new user
    cur.execute("""
        INSERT INTO users (first_name, last_name, email, phone, city, interest)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (first_name, last_name, email, phone, city, interest))
    cur.connection.commit()

    user_id = cur.lastrowid
    cur.close()

    # Create JWT token
    token = create_access_token(identity={
        'id': user_id,
        'email': email,
        'role': 'user',
        'name': first_name
    })

    return jsonify({
        'message': f'Welcome to WanderHub, {first_name}!',
        'token': token,
        'user': {
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'city': city,
            'interest': interest
        }
    }), 201


# ─────────────────────────────────────────
#   POST /api/auth/login
#   Login existing user (traveler)
# ─────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    name  = data.get('name', '').strip()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    cur = get_db_connection()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'error': 'No account found with this email. Please register first.'}), 404

    # Create JWT token
    token = create_access_token(identity={
        'id': user['id'],
        'email': user['email'],
        'role': 'user',
        'name': user['first_name']
    })

    return jsonify({
        'message': f"Welcome back, {user['first_name']}!",
        'token': token,
        'user': {
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'phone': user['phone'],
            'city': user['city'],
            'interest': user['interest']
        }
    }), 200


# ─────────────────────────────────────────
#   POST /api/auth/agency/login
#   Login for travel agencies
# ─────────────────────────────────────────
@auth_bp.route('/agency/login', methods=['POST'])
def agency_login():
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    cur = get_db_connection()
    cur.execute("SELECT * FROM agencies WHERE email = %s", (email,))
    agency = cur.fetchone()
    cur.close()

    if not agency:
        return jsonify({'error': 'Agency not found'}), 404

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), agency['password'].encode('utf-8')):
        return jsonify({'error': 'Incorrect password'}), 401

    token = create_access_token(identity={
        'id': agency['id'],
        'email': agency['email'],
        'role': 'agency',
        'name': agency['agency_name']
    })

    return jsonify({
        'message': f"Welcome, {agency['agency_name']}!",
        'token': token,
        'agency': {
            'id': agency['id'],
            'agency_name': agency['agency_name'],
            'owner_name': agency['owner_name'],
            'email': agency['email'],
            'phone': agency['phone'],
            'city': agency['city'],
            'rating': str(agency['rating']),
            'verified': agency['verified']
        }
    }), 200


# ─────────────────────────────────────────
#   POST /api/auth/agency/register
#   Register new travel agency
# ─────────────────────────────────────────
@auth_bp.route('/agency/register', methods=['POST'])
def agency_register():
    data         = request.get_json()
    agency_name  = data.get('agency_name', '').strip()
    owner_name   = data.get('owner_name', '').strip()
    email        = data.get('email', '').strip().lower()
    phone        = data.get('phone', '').strip()
    city         = data.get('city', '').strip()
    spec         = data.get('specialization', '').strip()
    password     = data.get('password', '')

    if not agency_name or not email or not password:
        return jsonify({'error': 'Agency name, email and password are required'}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = get_db_connection()
    cur.execute("SELECT id FROM agencies WHERE email = %s", (email,))
    if cur.fetchone():
        return jsonify({'error': 'Agency with this email already exists'}), 409

    cur.execute("""
        INSERT INTO agencies (agency_name, owner_name, email, phone, city, password, specialization)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (agency_name, owner_name, email, phone, city, hashed, spec))
    cur.connection.commit()
    agency_id = cur.lastrowid
    cur.close()

    token = create_access_token(identity={
        'id': agency_id,
        'email': email,
        'role': 'agency',
        'name': agency_name
    })

    return jsonify({
        'message': f'Agency "{agency_name}" registered successfully!',
        'token': token,
        'agency': {
            'id': agency_id,
            'agency_name': agency_name,
            'email': email
        }
    }), 201
