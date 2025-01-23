from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from functools import wraps
import datetime

def login():
    """
    User login
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: The user's email
            password:
              type: string
              description: The user's password
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
            access_token:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
    security: []
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM "user" WHERE email = %s', (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['id']), expires_delta=datetime.timedelta(hours=1))
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@jwt_required()
def get_logged_user():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, email, email_confirmed, active, created_at FROM "user" WHERE id = %s', (current_user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user

def login_required(fn, optional_message="You must be logged in to access this resource"):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            c = verify_jwt_in_request()
            print(c)
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Unauthorized", "message": optional_message}), 401
    return wrapper

def anonymous_required(fn, optional_message="You must be logged out to access this resource"):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return jsonify({"error": "Already logged in", "message": optional_message}), 400
        except Exception:
            return fn(*args, **kwargs)
    return wrapper

def verify_identity(user_id, optional_message="You can't perform this action"):
    current_user_id = int(get_jwt_identity())
    checking_user_id = int(user_id)
    if current_user_id != checking_user_id:
        return jsonify({"error": "Unauthorized", "message": optional_message}), 403
    return None