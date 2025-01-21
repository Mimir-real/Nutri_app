from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection

def login():
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

    if user and user['password'] == password:
        access_token = "test_token"  # create_access_token(identity=user['id'])
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401