from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from config.db import mysql
from middleware.auth_middleware import user_required

users_bp = Blueprint('users', __name__)

# ─────────────────────────────────────────
#   GET /api/users/profile
#   Get logged-in user's profile
# ─────────────────────────────────────────
@users_bp.route('/profile', methods=['GET'])
@user_required
def get_profile():
    identity = get_jwt_identity()
    user_id  = identity['id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, first_name, last_name, email, phone, city, interest, created_at FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user}), 200


# ─────────────────────────────────────────
#   PUT /api/users/profile
#   Update user profile
# ─────────────────────────────────────────
@users_bp.route('/profile', methods=['PUT'])
@user_required
def update_profile():
    identity = get_jwt_identity()
    user_id  = identity['id']
    data     = request.get_json()

    allowed = ['first_name', 'last_name', 'phone', 'city', 'interest']
    updates, params = [], []

    for f in allowed:
        if f in data:
            updates.append(f"{f} = %s")
            params.append(data[f])

    if not updates:
        return jsonify({'error': 'Nothing to update'}), 400

    params.append(user_id)
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", params)
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Profile updated successfully'}), 200


# ─────────────────────────────────────────
#   POST /api/users/search-history
#   Save a search query to history
# ─────────────────────────────────────────
@users_bp.route('/search-history', methods=['POST'])
@user_required
def save_search():
    identity = get_jwt_identity()
    user_id  = identity['id']
    data     = request.get_json()
    query    = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    cur = mysql.connection.cursor()
    # Avoid duplicate recent searches
    cur.execute("""
        SELECT id FROM search_history
        WHERE user_id = %s AND query = %s
        ORDER BY searched_at DESC LIMIT 1
    """, (user_id, query))
    existing = cur.fetchone()

    if existing:
        cur.execute("UPDATE search_history SET searched_at = NOW() WHERE id = %s", (existing['id'],))
    else:
        cur.execute("INSERT INTO search_history (user_id, query) VALUES (%s, %s)", (user_id, query))

    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Search saved'}), 200


# ─────────────────────────────────────────
#   GET /api/users/search-history
#   Get user's search history
# ─────────────────────────────────────────
@users_bp.route('/search-history', methods=['GET'])
@user_required
def get_search_history():
    identity = get_jwt_identity()
    user_id  = identity['id']

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT query, searched_at FROM search_history
        WHERE user_id = %s
        ORDER BY searched_at DESC
        LIMIT 10
    """, (user_id,))
    history = cur.fetchall()
    cur.close()

    return jsonify({'history': history}), 200


# ─────────────────────────────────────────
#   DELETE /api/users/search-history
#   Clear all search history
# ─────────────────────────────────────────
@users_bp.route('/search-history', methods=['DELETE'])
@user_required
def clear_search_history():
    identity = get_jwt_identity()
    user_id  = identity['id']

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM search_history WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Search history cleared'}), 200
