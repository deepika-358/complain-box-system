from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

try:
    from backend.models import User
    from backend.database import db
except ImportError:
    from models import User
    from database import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity={"id": user.id, "role": user.role, "username": user.username})
    return jsonify({
        "token": token,
        "user": user.to_dict(),
    })


@auth_bp.route("/api/auth/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@auth_bp.route("/api/auth/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409
    user = User(username=data["username"], email=data["email"], role=data.get("role", "staff"))
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user": user.to_dict()}), 201
