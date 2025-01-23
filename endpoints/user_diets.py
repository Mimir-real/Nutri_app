from flask import request, jsonify
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity

@login_required
def assign_diet_to_user(user_id):
    """
    Assign a diet to a user
    ---
    tags:
      - User Diets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to assign the diet to
      - in: body
        name: body
        schema:
          type: object
          required:
            - diet_id
          properties:
            diet_id:
              type: integer
              description: The ID of the diet to assign
            allowed:
              type: boolean
              description: Whether the diet is allowed
              default: true
    responses:
      201:
        description: Diet assigned to user
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
        description: User or diet not found
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
        verifivation = verify_identity(user_id, 'You can only assign diets to yourself')
        if verifivation is not None:
            return verifivation

        data = request.get_json()
        if not user_id or not data.get('diet_id'):
            return jsonify({"error": "diet_id is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT id FROM "user" WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404

        cursor.execute('SELECT id FROM diet WHERE id = %s', (data['diet_id'],))
        diet = cursor.fetchone()
        if not diet:
            cursor.close()
            conn.close()
            return jsonify({"message": "Diet not found"}), 404

        allowed = data.get('allowed', True)  # Default to True if 'allowed' is not provided

        try:
            cursor.execute('''
                INSERT INTO user_diets (user_id, diet_id, allowed)
                VALUES (%s, %s, %s)
            ''', (user_id, data['diet_id'], allowed))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "This user already has this diet assigned"}), 400

        cursor.close()
        conn.close()
        return jsonify({"message": "Diet assigned to user"}), 201

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def remove_diet_from_user(user_id, diet_id):
    """
    Remove a diet from a user
    ---
    tags:
      - User Diets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to remove the diet from
      - in: path
        name: diet_id
        type: integer
        required: true
        description: The ID of the diet to remove
    responses:
      200:
        description: Diet removed from user
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: User diet not found
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
        verifivation = verify_identity(user_id, 'You can only remove diets from yourself')
        if verifivation is not None:
            return verifivation

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('''
            SELECT id FROM user_diets
            WHERE user_id = %s AND diet_id = %s
        ''', (user_id, diet_id))
        user_diet = cursor.fetchone()
        if not user_diet:
            cursor.close()
            conn.close()
            return jsonify({"error": "User diet not found"}), 404

        cursor.execute('''
            DELETE FROM user_diets
            WHERE user_id = %s AND diet_id = %s
        ''', (user_id, diet_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Diet removed from user"})

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

def get_user_diets(user_id):
    """
    Get diets for a user
    ---
    tags:
      - User Diets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve diets for
    responses:
      200:
        description: A list of user diets
        schema:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
              diet_id:
                type: integer
              allowed:
                type: boolean
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

        cursor.execute('''
            SELECT * FROM user_diets
            WHERE user_id = %s
        ''', (user_id,))
        user_diets = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(user_diets)

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500