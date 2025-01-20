from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from models import User, db

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
# Dlaczego register jak jest users.py -> create_user
def register():
    pass
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({"error": "Email and password are required"}), 400

#     if User.query.filter_by(email=email).first():
#         return jsonify({"error": "User with this email already exists"}), 400

#     hashed_password = generate_password_hash(password)
#     new_user = User(email=email, password=hashed_password)
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({"message": "User registered successfully"}), 201