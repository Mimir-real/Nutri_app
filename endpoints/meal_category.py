from flask import request, jsonify
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity
import datetime
from endpoints.meal_history import create_meal_history

@login_required
def get_meal_categories():
    """
    Get all meal categories
    ---
    tags:
      - Meal Categories
    security:
      - Bearer: []
    responses:
      200:
        description: A list of meal categories
        schema:
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

        cursor.execute('SELECT * FROM meal_category')
        categories = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([dict(category) for category in categories])
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def assign_category_to_meal(meal_id, category_id):
    """
    Assign a category to a meal
    ---
    tags:
      - Meal Categories
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to assign the category to
      - in: path
        name: category_id
        type: integer
        required: true
        description: The ID of the category to assign
    responses:
      200:
        description: Category assigned to meal
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
        description: Meal or category not found
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
        
        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        if meal['category_id'] is not None:
            cursor.close()
            conn.close()
            return jsonify({"error": "Category is already assigned to this meal"}), 400

        cursor.execute('SELECT * FROM meal_category WHERE id = %s', (category_id,))
        category = cursor.fetchone()
        if not category:
            cursor.close()
            conn.close()
            return jsonify({"message": "Category not found"}), 404

        cursor.execute('''
            UPDATE meal
            SET category_id = %s, version = version + 1, last_update = %s
            WHERE id = %s
        ''', (category['id'], datetime.datetime.utcnow().isoformat(), meal_id))
        conn.commit()

        create_meal_history(cursor, meal_id)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category assigned to meal"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def remove_category_from_meal(meal_id):
    """
    Remove a category from a meal
    ---
    tags:
      - Meal Categories
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to remove the category from
    responses:
      200:
        description: Category removed from meal
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

        if meal['category_id'] is None:
            cursor.close()
            conn.close()
            return jsonify({"error": "No category assigned to this meal"}), 400

        cursor.execute('''
            UPDATE meal
            SET category_id = NULL, version = version + 1, last_update = %s
            WHERE id = %s
        ''', (datetime.datetime.utcnow().isoformat(), meal_id))
        conn.commit()

        create_meal_history(cursor, meal_id)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category removed from meal"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def update_category_of_meal(meal_id, category_id):
    """
    Update the category of a meal
    ---
    tags:
      - Meal Categories
    security:
      - Bearer: []
    parameters:
      - in: path
        name: meal_id
        type: integer
        required: true
        description: The ID of the meal to update the category for
      - in: path
        name: category_id
        type: integer
        required: true
        description: The ID of the new category
    responses:
      200:
        description: Category updated for meal
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
        description: Meal or category not found
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

        verifivation = verify_identity(meal['creator_id'], 'You can only edit meals you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        cursor.execute('SELECT * FROM meal_category WHERE id = %s', (category_id,))
        category = cursor.fetchone()
        if not category:
            cursor.close()
            conn.close()
            return jsonify({"message": "Category not found"}), 404

        cursor.execute('''
            UPDATE meal
            SET category_id = %s, version = version + 1, last_update = %s
            WHERE id = %s
        ''', (category['id'], datetime.datetime.utcnow().isoformat(), meal_id))
        conn.commit()

        create_meal_history(cursor, meal_id)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category updated for meal"}), 200
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500