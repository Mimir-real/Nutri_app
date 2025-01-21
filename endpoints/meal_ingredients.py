from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection

def get_meal_ingredients(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('''
        SELECT mi.*, i.*
        FROM meal_ingredients mi
        JOIN ingredients i ON mi.ingredient_id = i.id
        WHERE mi.meal_id = %s
    ''', (meal_id,))
    results = cursor.fetchall()

    ingredients = []
    for result in results:
        ingredient_dict = {
            'ingredient': {
                'id': result['id'],
                'product_name': result['product_name'],
                'generic_name': result['generic_name'],
                'kcal_100g': result['kcal_100g'],
                'protein_100g': result['protein_100g'],
                'carbs_100g': result['carbs_100g'],
                'fat_100g': result['fat_100g'],
                'brand': result['brand'],
                'barcode': result['barcode'],
                'image_url': result['image_url'],
                'labels_tags': result['labels_tags'],
                'product_quantity': result['product_quantity'],
                'allergens': result['allergens'],
                'tsv': result['tsv']
            },
            'details': {
                'meal_id': result['meal_id'],
                'ingredient_id': result['ingredient_id'],
                'unit': result['unit'],
                'quantity': result['quantity']
            }
        }
        ingredients.append(ingredient_dict)

    cursor.close()
    conn.close()

    return jsonify(ingredients)

def replace_meal_ingredients(meal_id):
    data = request.get_json()

    if data.get('ingredients') is None:
        return jsonify({"error": "Ingredients list is required"}), 400
    ingredients = data['ingredients']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (meal_id, meal['version'], dict(meal)))

    cursor.execute('DELETE FROM meal_ingredients WHERE meal_id = %s', (meal_id,))

    for ingredient_data in ingredients:
        cursor.execute('''
            INSERT INTO meal_ingredients (meal_id, ingredient_id, unit, quantity)
            VALUES (%s, %s, %s, %s)
        ''', (meal_id, ingredient_data['ingredient_id'], ingredient_data['unit'], ingredient_data['quantity']))

    cursor.execute('''
        UPDATE meal
        SET version = version + 1
        WHERE id = %s
    ''', (meal_id,))

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (meal_id, meal['version'] + 1, data))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Meal ingredients updated successfully"}), 200

def add_meal_ingredient(meal_id):
    data = request.get_json()

    if not data.get('ingredient_id') or not data.get('unit') or not data.get('quantity'):
        return jsonify({"error": "ingredient_id, unit, and quantity are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (meal_id, meal['version'], dict(meal)))

    try:
        cursor.execute('''
            INSERT INTO meal_ingredients (meal_id, ingredient_id, unit, quantity)
            VALUES (%s, %s, %s, %s)
        ''', (meal_id, data['ingredient_id'], data['unit'], data['quantity']))
        cursor.execute('''
            UPDATE meal
            SET version = version + 1
            WHERE id = %s
        ''', (meal_id,))
        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'] + 1, data))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": "This ingredient is already assigned to the meal"}), 400

    cursor.close()
    conn.close()

    return jsonify({"message": "Ingredient added successfully"}), 201

def remove_meal_ingredient(meal_id, ingredient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal_ingredients WHERE meal_id = %s AND ingredient_id = %s', (meal_id, ingredient_id))
    ingredient = cursor.fetchone()
    if not ingredient:
        cursor.close()
        conn.close()
        return jsonify({"error": "Ingredient not found in meal"}), 404

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (meal_id, meal['version'], dict(meal)))

    try:
        cursor.execute('DELETE FROM meal_ingredients WHERE meal_id = %s AND ingredient_id = %s', (meal_id, ingredient_id))
        cursor.execute('''
            UPDATE meal
            SET version = version + 1
            WHERE id = %s
        ''', (meal_id,))
        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'] + 1, dict(meal)))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": "Failed to remove ingredient"}), 400

    cursor.close()
    conn.close()

    return jsonify({"message": "Ingredient removed successfully"}), 200