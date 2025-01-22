from flask import request, jsonify
import datetime
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor
from endpoints.auth import login_required, verify_identity
from flask_jwt_extended import get_jwt_identity
import json

@login_required
def get_meals():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT COUNT(*) AS count FROM meal')
        total = cursor.fetchone()['count']

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def get_meal(meal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def search_meals():
    query = request.args.get('query', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    allow_more = request.args.get('allowMore', default=False, type=bool)
    user_id = request.args.get('user_id', type=int) if request.args.get('user_id') else get_jwt_identity()

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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

        cursor.execute(f'SELECT COUNT(*) AS count FROM meal WHERE {filters}', params)
        total = cursor.fetchone()['count']

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def create_meal():
    data = request.get_json()

    if not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    
    creator_id = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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
        ''', (data.get('name'), data.get('description', ""), creator_id, diet_id, category_id, 1, datetime.datetime.utcnow()))
        new_meal_id = cursor.fetchone()['id']

        ingredients = data.get('ingredients', [])
        for ingredient in ingredients:
            cursor.execute('''
                INSERT INTO meal_ingredients (meal_id, ingredient_id, unit, quantity)
                VALUES (%s, %s, %s, %s)
            ''', (new_meal_id, ingredient['ingredient_id'], ingredient['unit'], ingredient['quantity']))

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (new_meal_id, 1, json.dumps(data)))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Meal created", "meal_id": new_meal_id}), 201

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def update_meal(meal_id):
    data = request.get_json()

    if data.get('ingredients'):
        return jsonify({"error": "To update ingredients, use the /meals/<meal_id>/ingredients endpoint"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()

        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404
        
        creator_id = meal['creator_id']
        verifivation = verify_identity(creator_id, 'You can only update meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        # Convert datetime objects to strings
        meal['last_update'] = meal['last_update'].isoformat() if meal['last_update'] else None

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'], json.dumps(meal)))

        cursor.execute('''
            UPDATE meal
            SET name = %s, description = %s, diet_id = %s, category_id = %s, version = version + 1, last_update = %s
            WHERE id = %s
        ''', (data.get('name', meal['name']), data.get('description', meal['description']), data.get('diet_id', meal['diet_id']), data.get('category_id', meal['category_id']), datetime.datetime.utcnow().isoformat(), meal_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Meal updated", "meal_id": meal_id}), 200

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Usuwanie wymaga więcej uwagi - relacje z MealHistory itp. - brak dostępu dla użytkownika
@login_required
def delete_meal(meal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()

        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404

        creator_id = meal['creator_id']
        verifivation = verify_identity(creator_id, 'You can only delete meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        cursor.execute('DELETE FROM meal WHERE id = %s', (meal_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Meal deleted"}), 200

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def get_meal_versions(meal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal_history WHERE meal_id = %s', (meal_id,))
        meal_versions = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "meal_versions": [dict(meal_version) for meal_version in meal_versions]
        })

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def get_meal_nutrients(meal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500