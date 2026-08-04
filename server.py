from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import database and routes from root directory
from db import init_db
from auth import auth_bp
from tours import tours_bp
from users import users_bp

# ─────────────────────────────────────────
#   Create Flask App
# ─────────────────────────────────────────
app = Flask(__name__)

# ── Config ──
app.config['SECRET_KEY']             = os.getenv('SECRET_KEY', 'wanderhub_secret')
app.config['JWT_SECRET_KEY']         = os.getenv('JWT_SECRET_KEY', 'wanderhub_jwt_secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token never expires (change in production)

# ── Extensions ──
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000'), 'null', '*'])
jwt  = JWTManager(app)
db   = init_db(app)

# ── Register Blueprints (routes) ──
app.register_blueprint(auth_bp,  url_prefix='/api/auth')
app.register_blueprint(tours_bp, url_prefix='/api/tours')
app.register_blueprint(users_bp, url_prefix='/api/users')

# ─────────────────────────────────────────
#   Root health check
# ─────────────────────────────────────────
@app.route('/')
def index():
    return jsonify({
        'message': 'WanderHub API is running! 🌍',
        'version': '1.0.0',
        'endpoints': {
            'auth':  '/api/auth',
            'tours': '/api/tours',
            'users': '/api/users'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Server is healthy'}), 200

# ─────────────────────────────────────────
#   JWT Error Handlers
# ─────────────────────────────────────────
@jwt.unauthorized_loader
def unauthorized(reason):
    return jsonify({'error': 'Login required', 'reason': reason}), 401

@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify({'error': 'Invalid token', 'reason': reason}), 422

# ─────────────────────────────────────────
#   Run Server
# ─────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    print(f"\n🚀 WanderHub Backend running on http://localhost:{port}")
    print(f"📋 API Docs:")
    print(f"   POST /api/auth/register        → User registration")
    print(f"   POST /api/auth/login           → User login")
    print(f"   POST /api/auth/agency/login    → Agency login")
    print(f"   POST /api/auth/agency/register → Agency registration")
    print(f"   GET  /api/tours                → Get all tours")
    print(f"   GET  /api/tours/<id>           → Get tour detail")
    print(f"   POST /api/tours                → Add tour (agency)")
    print(f"   PUT  /api/tours/<id>           → Update tour (agency)")
    print(f"   DELETE /api/tours/<id>         → Delete tour (agency)")
    print(f"   GET  /api/users/profile        → User profile")
    print(f"   POST /api/users/search-history → Save search\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
