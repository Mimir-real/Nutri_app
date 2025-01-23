from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity
import json
import datetime

@login_required
def get_meal_ingredients(meal_id):
    """
    Get ingredients for a meal
    ---
    tags:
      - Meal Ingredients
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to retrieve ingredients for
    responses:
      200:
        description: A list of ingredients for the meal
        schema:
          type: array
          items:
            type: object
            properties:
              ingredient:
                type: object
                properties:
                  id:
                    type: integer
                  product_name:
                    type: string
                  generic_name:
                    type: string
                  kcal_100g:
                    type: number
                  protein_100g:
                    type: number
                  carbs_100g:
                    type: number
                  fat_100g:
                    type: number
                  brand:
                    type: string
                  barcode:
                    type: string
                  image_url:
                    type: string
                  labels_tags:
                    type: string
                  product_quantity:
                    type: number
                  allergens:
                    type: string
              details:
                type: object
                properties:
                  meal_id:
                    type: integer
                  ingredient_id:
                    type: integer
                  unit:
                    type: string
                  quantity:
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
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def replace_meal_ingredients(meal_id):
    """
    Replace ingredients for a meal
    ---
    tags:
      - Meal Ingredients
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to replace ingredients for
      - in: body
        name: body
        schema:
          type: object
          required:
            - ingredients
          properties:
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
      200:
        description: Meal ingredients updated successfully
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
        data = request.get_json()

        if data.get('ingredients') is None:
            return jsonify({"error": "Ingredients list is required"}), 400
        ingredients = data['ingredients']

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM meal WHERE id = %s', (meal_id,))
        meal = cursor.fetchone()
        if not meal:
            cursor.close()
            conn.close()
            return jsonify({"message": "Meal not found"}), 404

        verifivation = verify_identity(meal['creator_id'], 'You can only delete meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        # Convert datetime objects to strings
        meal['last_update'] = meal['last_update'].isoformat() if meal['last_update'] else None

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'], json.dumps(dict(meal))))

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

        # Convert datetime objects to strings in the new data
        data['last_update'] = datetime.datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'] + 1, json.dumps(data)))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Meal ingredients updated successfully"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def add_meal_ingredient(meal_id):
    """
    Add an ingredient to a meal
    ---
    tags:
      - Meal Ingredients
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to add the ingredient to
      - in: body
        name: body
        schema:
          type: object
          required:
            - ingredient_id
            - unit
            - quantity
          properties:
            ingredient_id:
              type: integer
              description: The ID of the ingredient to add
            unit:
              type: string
              description: The unit of the ingredient
            quantity:
              type: number
              description: The quantity of the ingredient
    responses:
      201:
        description: Ingredient added successfully
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
        data = request.get_json()

        if not data.get('ingredient_id') or not data.get('unit') or not data.get('quantity'):
            return jsonify({"error": "ingredient_id, unit, and quantity are required"}), 400

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

        # Convert datetime objects to strings
        meal['last_update'] = meal['last_update'].isoformat() if meal['last_update'] else None

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'], json.dumps(dict(meal))))

        try:
            cursor.execute('''
                INSERT INTO meal_ingredients (meal_id, ingredient_id, unit, quantity)
                VALUES (%s, %s, %s, %s)
            ''', (meal_id, data['ingredient_id'], data['unit'], data['quantity']))
            cursor.execute('''
                UPDATE meal
                SET version = version + 1, last_update = %s
                WHERE id = %s
            ''', (datetime.datetime.utcnow().isoformat(), meal_id))
            cursor.execute('''
                INSERT INTO meal_history (meal_id, meal_version, composition)
                VALUES (%s, %s, %s)
            ''', (meal_id, meal['version'] + 1, json.dumps(data)))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "This ingredient is already assigned to the meal"}), 400

        cursor.close()
        conn.close()

        return jsonify({"message": "Ingredient added successfully"}), 201
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def remove_meal_ingredient(meal_id, ingredient_id):
    """
    Remove an ingredient from a meal
    ---
    tags:
      - Meal Ingredients
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to remove the ingredient from
      - in: path
        name: ingredient_id
        type: integer
        required: true
        description: The ID of the ingredient to remove
    responses:
      200:
        description: Ingredient removed successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Ingredient not found in meal
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
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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
        
        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        # Convert datetime objects to strings
        meal['last_update'] = meal['last_update'].isoformat() if meal['last_update'] else None

        cursor.execute('''
            INSERT INTO meal_history (meal_id, meal_version, composition)
            VALUES (%s, %s, %s)
        ''', (meal_id, meal['version'], json.dumps(dict(meal))))

        try:
            cursor.execute('DELETE FROM meal_ingredients WHERE meal_id = %s AND ingredient_id = %s', (meal_id, ingredient_id))
            cursor.execute('''
                UPDATE meal
                SET version = version + 1, last_update = %s
                WHERE id = %s
            ''', (datetime.datetime.utcnow().isoformat(), meal_id))
            cursor.execute('''
                INSERT INTO meal_history (meal_id, meal_version, composition)
                VALUES (%s, %s, %s)
            ''', (meal_id, meal['version'] + 1, json.dumps(dict(meal))))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Failed to remove ingredient"}), 400

        cursor.close()
        conn.close()

        return jsonify({"message": "Ingredient removed successfully"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500