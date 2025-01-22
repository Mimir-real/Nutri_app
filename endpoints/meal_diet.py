from flask import request, jsonify
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor
from endpoints.auth import login_required, verify_identity

@login_required
def assign_diet_to_meal(meal_id):
    try:
        data = request.get_json()
        if not data.get('diet_id'):
            return jsonify({"error": "diet_id is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()
        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404
        
        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        if meal['diet_id'] is not None:
            cursor.close()
            conn.close()
            return jsonify({"error": "Diet is already assigned to this meal"}), 400

        cursor.execute('SELECT * FROM diet WHERE id = %s', (data['diet_id'],))
        diet = cursor.fetchone()
        if not diet:
            cursor.close()
            conn.close()
            return jsonify({"message": "Diet not found"}), 404

        cursor.execute('''
            UPDATE meal
            SET diet_id = %s, version = version + 1
            WHERE id = %s
        ''', (diet['id'], meal_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Diet assigned to meal"}), 200

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def remove_diet_from_meal(meal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()
        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404

        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        if meal['diet_id'] is None:
            cursor.close()
            conn.close()
            return jsonify({"error": "No diet assigned to this meal"}), 400

        cursor.execute('''
            UPDATE meal
            SET diet_id = NULL, version = version + 1
            WHERE id = %s
        ''', (meal_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Diet removed from meal"}), 200

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def update_diet_of_meal(meal_id):
    try:
        data = request.get_json()
        if not data.get('diet_id'):
            return jsonify({"error": "diet_id is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()
        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404
        
        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        if meal['diet_id'] is None:
            cursor.close()
            conn.close()
            return jsonify({"error": "No diet assigned to this meal"}), 400

        cursor.execute('SELECT * FROM diet WHERE id = %s', (data['diet_id'],))
        diet = cursor.fetchone()
        if not diet:
            cursor.close()
            conn.close()
            return jsonify({"message": "Diet not found"}), 404

        cursor.execute('''
            UPDATE meal
            SET diet_id = %s, version = version + 1
            WHERE id = %s
        ''', (diet['id'], meal_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Diet updated for meal"}), 200

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500