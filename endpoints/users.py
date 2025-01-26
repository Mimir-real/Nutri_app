from db_config import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
import uuid
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from endpoints.auth import get_logged_user, login_required, anonymous_required, verify_identity
import datetime

@login_required
def get_me():
    """
    Get current user
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: A user object
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            email_confirmed:
              type: boolean
            active:
              type: boolean
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        user = get_logged_user()
        if isinstance(user, dict) and "error" in user:
            return jsonify(user), 403

        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@anonymous_required
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
            - confirm_password
          properties:
            email:
              type: string
              description: The user's email
            password:
              type: string
              description: The user's password
            confirm_password:
              type: string
              description: The user's password confirmation
    responses:
      201:
        description: User created
        schema:
          type: object
          properties:
            message:
              type: string
            user_id:
              type: integer
            activation_code:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
            message:
              type: string
    security: []
    """
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password') or not data.get('confirm_password'):
            raise ValueError("Email, password, and password confirmation are required")

        if data['password'] != data['confirm_password']:
            raise ValueError("Passwords do not match")

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if email is unique
        cursor.execute('SELECT id FROM "user" WHERE email = %s', (data['email'],))
        if cursor.fetchone():
            raise ValueError("Email already exists")

        hashed_password = generate_password_hash(data['password'])

        cursor.execute('''
            INSERT INTO "user" (email, password, email_confirmed, active, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        ''', (data['email'], hashed_password, False, False))
        new_user_id = cursor.fetchone()['id']

        activation_code = str(uuid.uuid4())
        expire_at = datetime.datetime.now() + datetime.timedelta(hours=24)

        cursor.execute('''
            INSERT INTO links (user_id, code, type_id, used, expire_at)
            VALUES (%s, %s, (SELECT id FROM link_types WHERE type = 'activate'), %s, %s)
        ''', (new_user_id, activation_code, False, expire_at))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User created", "user_id": new_user_id, "activation_code": activation_code}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "User with this email already exists"}), 400
    
    except Exception as e:
        return jsonify({"error": "An error occurred while creating the user", "message": str(e)}), 500

@login_required
def get_users():
    """
    Get a list of users
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of users to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
    responses:
      200:
        description: A list of users
        schema:
          type: object
          properties:
            users:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  email:
                    type: string
                  email_confirmed:
                    type: boolean
                  active:
                    type: boolean
                  created_at:
                    type: string
                    format: date-time
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
            page_size:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
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
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def get_user(user_id):
    """
    Get a user by ID
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve
    responses:
      200:
        description: A user object
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            email_confirmed:
              type: boolean
            active:
              type: boolean
            created_at:
              type: string
              format: date-time
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
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
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@anonymous_required
def activate_user(user_id):
    """
    Activate a user
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to activate
      - in: query
        name: code
        type: string
        required: true
        description: Activation code
      - in: query
        name: email
        type: string
        required: true
        description: User's email
    responses:
      200:
        description: User activated successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    security: []
    """
    try:
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

        cursor.execute('''
            SELECT links.id, links.expire_at, links.type_id
            FROM links
            JOIN link_types ON links.type_id = link_types.id
            WHERE links.user_id = %s AND links.code = %s AND link_types.type = 'activate'
        ''', (user_id, code))
        link = cursor.fetchone()

        if not link:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid code"}), 400

        if link['expire_at'] and link['expire_at'] < datetime.datetime.now():
            cursor.execute('DELETE FROM links WHERE id = %s', (link['id'],))
            cursor.execute('DELETE FROM "user" WHERE id = %s', (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"error": "Link expired and user deleted"}), 400

        cursor.execute('UPDATE "user" SET active = %s, email_confirmed = %s WHERE id = %s', (True, True, user_id))
        cursor.execute('DELETE FROM links WHERE id = %s', (link['id'],))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User activated successfully"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    
@login_required
def deactivate_user(user_id):
    """
    Deactivate a user
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to deactivate
      - in: body
        name: body
        schema:
          type: object
          required:
            - password
          properties:
            password:
              type: string
              description: The user's password
    responses:
      200:
        description: User deactivated
        schema:
          type: object
          properties:
            message:
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
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        verifivation = verify_identity(user_id, 'You can only deactivate yourself')
        if verifivation is not None:
            return verifivation

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
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500