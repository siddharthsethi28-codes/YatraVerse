from flask import Flask
from flask_cors import CORS
from db import get_db_connection
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')

# Test database connection on startup
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "message": "Server & DB connection healthy!"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/', methods=['GET'])
def root():
    return {
        "message": "WanderHub API is running! 🌍",
        "version": "1.0.0"
    }, 200

# Import and register blueprints
from auth import auth_bp
from tours import tours_bp
from users import users_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(tours_bp, url_prefix='/api/tours')
app.register_blueprint(users_bp, url_prefix='/api/users')

if __name__ == '__main__':
    app.run(debug=True)
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
