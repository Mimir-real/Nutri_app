from flask import request, jsonify
import datetime
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor
from endpoints.auth import login_required, verify_identity
from flask_jwt_extended import get_jwt_identity
import json
from endpoints.meal_history import create_meal_history

@login_required
def get_meals():
    """
    Get a list of meals
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of meals to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
    responses:
      200:
        description: A list of meals
        schema:
          type: object
          properties:
            meals:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
                  creator_id:
                    type: integer
                  diet_id:
                    type: integer
                  category_id:
                    type: integer
                  version:
                    type: integer
                  last_update:
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
    """
    Get a meal by ID
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to retrieve
    responses:
      200:
        description: A meal object
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            creator_id:
              type: integer
            diet_id:
              type: integer
            category_id:
              type: integer
            version:
              type: integer
            last_update:
              type: string
              format: date-time
      404:
        description: Meal not found
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
    """
    Search for meals
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: query
        name: query
        type: string
        description: The search query
        default: ''
      - in: query
        name: limit
        type: integer
        description: Number of meals to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
      - in: query
        name: allowMore
        type: boolean
        description: Whether to allow more results
        default: False
      - in: query
        name: user_id
        type: integer
        description: The ID of the user
    responses:
      200:
        description: A list of meals
        schema:
          type: object
          properties:
            meals:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
                  creator_id:
                    type: integer
                  diet_id:
                    type: integer
                  category_id:
                    type: integer
                  version:
                    type: integer
                  last_update:
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
    """
    Create a new meal
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: The name of the meal
            description:
              type: string
              description: The description of the meal
            diet_id:
              type: integer
              description: The ID of the diet
            category_id:
              type: integer
              description: The ID of the category
            ingredients:
              type: array
              items:
                type: object
                properties:
                  ingredient_id:
                    type: integer
                  unit:
                    type: string
                  quantity:
                    type: number
    responses:
      201:
        description: Meal created
        schema:
          type: object
          properties:
            message:
              type: string
            meal_id:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Category or diet not found
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
    """
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

        create_meal_history(cursor, new_meal_id)

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
    """
    Update a meal
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to update
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
              description: The name of the meal
            description:
              type: string
              description: The description of the meal
            diet_id:
              type: integer
              description: The ID of the diet
            category_id:
              type: integer
              description: The ID of the category
    responses:
      200:
        description: Meal updated
        schema:
          type: object
          properties:
            message:
              type: string
            meal_id:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Meal not found
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
            UPDATE meal
            SET name = %s, description = %s, diet_id = %s, category_id = %s, version = version + 1, last_update = %s
            WHERE id = %s
        ''', (data.get('name', meal['name']), data.get('description', meal['description']), data.get('diet_id', meal['diet_id']), data.get('category_id', meal['category_id']), datetime.datetime.utcnow().isoformat(), meal_id))

        create_meal_history(cursor, meal_id)

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
    """
    Delete a meal
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to delete
    responses:
      200:
        description: Meal deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Meal not found
        schema:
          type: object
          properties:
            message:
              type: string
      403:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
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
    """
    Get versions of a meal
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to retrieve versions for
    responses:
      200:
        description: A list of meal versions
        schema:
          type: array
          items:
            type: object
            properties:
              meal_id:
                type: integer
              meal_version:
                type: integer
              composition:
                type: string
      404:
        description: Meal not found
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
    """
    Get nutrients of a meal
    ---
    tags:
      - Meals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to retrieve nutrients for
    responses:
      200:
        description: Nutrients of the meal
        schema:
          type: object
          properties:
            nutrients:
              type: object
              properties:
                total_calories:
                  type: number
                total_protein:
                  type: number
                total_carbs:
                  type: number
                total_fat:
                  type: number
            nutrients_per_100g:
              type: object
              properties:
                calories:
                  type: number
                protein:
                  type: number
                carbs:
                  type: number
                fat:
                  type: number
      404:
        description: Meal not found
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