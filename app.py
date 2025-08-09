from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os

app = Flask(__name__)

# ✅ Allowed origins (NO trailing slash!)
allowed_origins = [
    "http://localhost:3000",
    "https://smart-inventory-frontend.vercel.app"
]

# ✅ CORS configuration for both local + production
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": allowed_origins}}
)

# ---------------- CONFIGURATION ----------------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')

# ✅ Render automatically sets DATABASE_URL to 'postgres://...' — fix it for SQLAlchemy
db_url = os.environ.get('DATABASE_URL', 'sqlite:///inventory.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=19)

jwt = JWTManager(app)
db = SQLAlchemy(app)
