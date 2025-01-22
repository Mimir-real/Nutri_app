from flask import request, jsonify
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity

@login_required
def assign_diet_to_user(user_id):
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