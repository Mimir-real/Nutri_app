from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection

def get_meal_categories():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM meal_category')
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([dict(category) for category in categories])

def assign_category_to_meal(meal_id):
    data = request.get_json()
    if not data.get('category_id'):
        return jsonify({"error": "category_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    if meal['category_id'] is not None:
        cursor.close()
        conn.close()
        return jsonify({"error": "Category is already assigned to this meal"}), 400

    cursor.execute('SELECT * FROM meal_category WHERE id = %s', (data['category_id'],))
    category = cursor.fetchone()
    if not category:
        cursor.close()
        conn.close()
        return jsonify({"message": "Category not found"}), 404

    cursor.execute('''
        UPDATE meal
        SET category_id = %s, version = version + 1
        WHERE id = %s
    ''', (category['id'], meal_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Category assigned to meal"}), 200

def remove_category_from_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    if meal['category_id'] is None:
        cursor.close()
        conn.close()
        return jsonify({"error": "No category assigned to this meal"}), 400

    cursor.execute('''
        UPDATE meal
        SET category_id = NULL, version = version + 1
        WHERE id = %s
    ''', (meal_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Category removed from meal"}), 200

def update_category_of_meal(meal_id):
    data = request.get_json()
    if not data.get('category_id'):
        return jsonify({"error": "category_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    if meal['category_id'] is None:
        cursor.close()
        conn.close()
        return jsonify({"error": "No category assigned to this meal"}), 400

    cursor.execute('SELECT * FROM meal_category WHERE id = %s', (data['category_id'],))
    category = cursor.fetchone()
    if not category:
        cursor.close()
        conn.close()
        return jsonify({"message": "Category not found"}), 404

    cursor.execute('''
        UPDATE meal
        SET category_id = %s, version = version + 1
        WHERE id = %s
    ''', (category['id'], meal_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Category updated for meal"}), 200