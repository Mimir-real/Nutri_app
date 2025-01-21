from flask import request, jsonify
from db_config import get_db_connection

def assign_diet_to_meal(meal_id):
    data = request.get_json()
    if not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

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

def remove_diet_from_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

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

def update_diet_of_meal(meal_id):
    data = request.get_json()
    if not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

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