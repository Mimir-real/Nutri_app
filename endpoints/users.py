from db_config import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
import uuid
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from endpoints.auth import get_logged_user, login_required, anonymous_required

@login_required
def get_me():
    user = get_logged_user()
    if isinstance(user, dict) and "error" in user:
        return jsonify(user), 403

    return jsonify(user)

@anonymous_required
def create_user():
    try:
        data = request.get_json()

        # Sprawdzamy, czy pola 'email' i 'password' są puste
        if not data.get('email') or not data.get('password'):
            raise ValueError("Email and password are required")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Hashujemy hasło
        hashed_password = generate_password_hash(data['password'])

        # Tworzymy nowego użytkownika
        cursor.execute('''
            INSERT INTO "user" (email, password, email_confirmed, active, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        ''', (data['email'], hashed_password, False, False))
        new_user_id = cursor.fetchone()[0]

        # Generate a unique activation code
        activation_code = str(uuid.uuid4())

        # Save the activation code in the Links table
        cursor.execute('''
            INSERT INTO links (user_id, code, type_id, used)
            VALUES (%s, %s, %s, %s)
        ''', (new_user_id, activation_code, 1, False))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User created", "user_id": new_user_id, "activation_code (wyświetlane dla celów prezentacyjnych)": activation_code}), 201

    except ValueError as e:
        print('POST /users - ValueError:', e)
        return jsonify({"error": str(e)}), 400
    
    except psycopg2.IntegrityError as e:
        print('POST /users - IntegrityError:', e)
        conn.rollback()
        return jsonify({"error": "User with this email already exists"}), 400
    
    except Exception as e:
        print('POST /users - Exception:', e)
        return jsonify({"error": "An error occurred while creating the user", "message": str(e)}), 500

@login_required
def get_users():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT COUNT(*) FROM "user"')
    total = cursor.fetchone()['count']

    cursor.execute('''
        SELECT id, email, email_confirmed, active, created_at
        FROM "user"
        ORDER BY id
        LIMIT %s OFFSET %s
    ''', (limit, offset))
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "users": users,
        "total": total,
        "pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_page": page,
        "page_size": limit
    })

@login_required
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, email, email_confirmed, active, created_at FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404

@anonymous_required
def activate_user(user_id):
    code = request.args.get('code')
    email = request.args.get('email')

    if not code or not email:
        return jsonify({"error": "Code and email are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, email FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if user['email'] != email:
        cursor.close()
        conn.close()
        return jsonify({"error": "Email does not match"}), 400

    cursor.execute('SELECT id FROM links WHERE user_id = %s AND code = %s', (user_id, code))
    link = cursor.fetchone()

    if not link:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid code"}), 400

    cursor.execute('UPDATE "user" SET active = %s, email_confirmed = %s WHERE id = %s', (True, True, user_id))
    cursor.execute('DELETE FROM links WHERE id = %s', (link['id'],))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User activated successfully"}), 200

@login_required
def deactivate_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != str(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, password FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user['password'], password):
        cursor.close()
        conn.close()
        return jsonify({"error": "Incorrect password"}), 401

    cursor.execute('UPDATE "user" SET active = %s WHERE id = %s', (False, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User deactivated"})