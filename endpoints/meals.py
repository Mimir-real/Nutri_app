from flask import request, jsonify
from datetime import datetime
from db_config import get_db_connection

def get_meals():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM meal')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT id, name, description, creator_id, diet_id, category_id, version, last_update
        FROM meal
        ORDER BY id
        LIMIT %s OFFSET %s
    ''', (limit, offset))
    meals = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "meals": [dict(meal) for meal in meals],
        "total": total,
        "pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_page": page,
        "page_size": limit
    })

def get_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, description, creator_id, diet_id, category_id, version, last_update
        FROM meal
        WHERE id = %s
    ''', (meal_id,))
    meal = cursor.fetchone()

    cursor.close()
    conn.close()

    if meal:
        return jsonify(dict(meal))
    else:
        return jsonify({"message": "Meal not found"}), 404

def search_meals():
    query = request.args.get('query', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    user_id = request.args.get('user_id', default=None, type=int)
    allow_more = request.args.get('allowMore', default=False, type=bool)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    filters = ['(name ILIKE %s OR description ILIKE %s)']
    params = [f'%{query}%', f'%{query}%']

    if user_id:
        if allow_more:
            filters.append('diet_id NOT IN (SELECT diet_id FROM user_diets WHERE user_id = %s AND allowed = FALSE)')
            params.append(user_id)
        else:
            filters.append('diet_id IN (SELECT diet_id FROM user_diets WHERE user_id = %s AND allowed = TRUE)')
            filters.append('diet_id NOT IN (SELECT diet_id FROM user_diets WHERE user_id = %s AND allowed = FALSE)')
            params.extend([user_id, user_id])

    filters = ' AND '.join(filters)

    cursor.execute(f'SELECT COUNT(*) FROM meal WHERE {filters}', params)
    total = cursor.fetchone()[0]

    cursor.execute(f'''
        SELECT id, name, description, creator_id, diet_id, category_id, version, last_update
        FROM meal
        WHERE {filters}
        ORDER BY id
        LIMIT %s OFFSET %s
    ''', params + [limit, offset])
    meals = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "meals": [dict(meal) for meal in meals],
        "total": total,
        "pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_page": page,
        "page_size": limit
    })

def create_meal():
    data = request.get_json()

    if not data.get('name') or not data.get('creator_id'):
        return jsonify({"error": "Name and creator_id are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    category_id = data.get('category_id')
    if category_id:
        cursor.execute('SELECT id FROM meal_category WHERE id = %s', (category_id,))
        category = cursor.fetchone()
        if not category:
            cursor.close()
            conn.close()
            return jsonify({"error": "Category not found"}), 404

    diet_id = data.get('diet_id')
    if diet_id:
        cursor.execute('SELECT id FROM diet WHERE id = %s', (diet_id,))
        diet = cursor.fetchone()
        if not diet:
            cursor.close()
            conn.close()
            return jsonify({"error": "Diet not found"}), 404

    cursor.execute('''
        INSERT INTO meal (name, description, creator_id, diet_id, category_id, version, last_update)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (data.get('name'), data.get('description', ""), data.get('creator_id'), diet_id, category_id, 1, datetime.utcnow()))
    new_meal_id = cursor.fetchone()[0]

    ingredients = data.get('ingredients', [])
    for ingredient in ingredients:
        cursor.execute('''
            INSERT INTO meal_ingredients (meal_id, ingredient_id, unit, quantity)
            VALUES (%s, %s, %s, %s)
        ''', (new_meal_id, ingredient['ingredient_id'], ingredient['unit'], ingredient['quantity']))

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (new_meal_id, 1, data))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Meal created", "meal_id": new_meal_id}), 201

def update_meal(meal_id):
    data = request.get_json()

    if data.get('ingredients'):
        return jsonify({"error": "To update ingredients, use the /meals/<meal_id>/ingredients endpoint"}), 400

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

    cursor.execute('''
        UPDATE meal
        SET name = %s, description = %s, diet_id = %s, category_id = %s, version = version + 1, last_update = %s
        WHERE id = %s
    ''', (data.get('name', meal['name']), data.get('description', meal['description']), data.get('diet_id', meal['diet_id']), data.get('category_id', meal['category_id']), datetime.utcnow(), meal_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Meal updated", "meal_id": meal_id}), 200

def delete_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    cursor.execute('DELETE FROM meal WHERE id = %s', (meal_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Meal deleted"})

def get_meal_versions(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal_history WHERE meal_id = %s', (meal_id,))
    meal_versions = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "meal_versions": [dict(meal_version) for meal_version in meal_versions]
    })

def get_meal_nutrients(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
    meal = cursor.fetchone()
    if not meal:
        cursor.close()
        conn.close()
        return jsonify({"message": "Meal not found"}), 404

    cursor.execute('SELECT * FROM meal_ingredients WHERE meal_id = %s', (meal_id,))
    ingredients = cursor.fetchall()

    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_weight = 0

    for ingredient in ingredients:
        cursor.execute('SELECT * FROM ingredients WHERE id = %s', (ingredient['ingredient_id'],))
        ingredient_details = cursor.fetchone()
        if not ingredient_details:
            continue

        quantity = ingredient['quantity']
        total_weight += quantity
        total_calories += ingredient_details['kcal_100g'] * quantity / 100
        total_protein += ingredient_details['protein_100g'] * quantity / 100
        total_carbs += ingredient_details['carbs_100g'] * quantity / 100
        total_fat += ingredient_details['fat_100g'] * quantity / 100

    cursor.close()
    conn.close()

    if total_weight == 0:
        return jsonify({"message": "No ingredients found for this meal"}), 404

    response = {
        "nutrients": {
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat
        },
        "nutrients_per_100g": {
            "calories": total_calories / total_weight * 100,
            "protein": total_protein / total_weight * 100,
            "carbs": total_carbs / total_weight * 100,
            "fat": total_fat / total_weight * 100
        }
    }

    return jsonify(response)