from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def user_required(fn):
    """Protect routes that need a logged-in user (traveler)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Login required'}), 401
    return wrapper

def agency_required(fn):
    """Protect routes that need a logged-in agency."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if identity.get('role') != 'agency':
                return jsonify({'error': 'Agency access only'}), 403
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Agency login required'}), 401
    return wrapper
