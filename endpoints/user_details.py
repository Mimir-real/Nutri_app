from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity

@login_required
def create_user_details(user_id):
    """
    Create user details
    ---
    tags:
      - User Details
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to create details for
      - in: body
        name: body
        schema:
          type: object
          required:
            - age
            - gender
            - height
            - weight
            - kcal_goal
            - fat_goal
            - protein_goal
            - carb_goal
          properties:
            age:
              type: integer
              description: The age of the user
            gender:
              type: string
              description: The gender of the user (F, M, X)
            height:
              type: number
              description: The height of the user
            weight:
              type: number
              description: The weight of the user
            kcal_goal:
              type: integer
              description: The daily calorie goal of the user
            fat_goal:
              type: integer
              description: The daily fat goal of the user
            protein_goal:
              type: integer
              description: The daily protein goal of the user
            carb_goal:
              type: integer
              description: The daily carbohydrate goal of the user
    responses:
      201:
        description: User details created successfully
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
        description: User not found
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
    verifivation = verify_identity(user_id, 'You can only create details for yourself')
    if verifivation is not None:
        return verifivation

    data = request.get_json()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT id FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User not found"}), 404

    cursor.execute('SELECT user_id FROM user_details WHERE user_id = %s', (user_id,))
    details = cursor.fetchone()
    if details:
        cursor.close()
        conn.close()
        return jsonify({"error": "User details already exist"}), 400

    gender = data.get('gender', 'X')
    if gender not in ['F', 'M', 'X']:
        return jsonify({"error": "Invalid gender value"}), 400

    age = data.get('age', 0)
    height = data.get('height', 0.0)
    weight = data.get('weight', 0.0)
    kcal_goal = data.get('kcal_goal', 0)
    fat_goal = data.get('fat_goal', 0)
    protein_goal = data.get('protein_goal', 0)
    carb_goal = data.get('carb_goal', 0)

    if any(value < 0 for value in [age, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal]):
        return jsonify({"error": "Age, height, weight, and goals must be greater than or equal to 0"}), 400

    cursor.execute('''
        INSERT INTO user_details (user_id, age, gender, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, age, gender, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User details created successfully"}), 201

@login_required
def update_user_details(user_id):
    """
    Update user details
    ---
    tags:
      - User Details
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to update details for
      - in: body
        name: body
        schema:
          type: object
          properties:
            age:
              type: integer
              description: The age of the user
            gender:
              type: string
              description: The gender of the user (F, M, X)
            height:
              type: number
              description: The height of the user
            weight:
              type: number
              description: The weight of the user
            kcal_goal:
              type: integer
              description: The daily calorie goal of the user
            fat_goal:
              type: integer
              description: The daily fat goal of the user
            protein_goal:
              type: integer
              description: The daily protein goal of the user
            carb_goal:
              type: integer
              description: The daily carbohydrate goal of the user
    responses:
      200:
        description: User details updated successfully
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
        description: User or user details not found
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
    verifivation = verify_identity(user_id, 'You can only update details for yourself')
    if verifivation is not None:
        return verifivation

    data = request.get_json()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT id FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User not found"}), 404

    cursor.execute('SELECT * FROM user_details WHERE user_id = %s', (user_id,))
    details = cursor.fetchone()
    if not details:
        cursor.close()
        conn.close()
        return jsonify({"message": "User details not found"}), 404

    gender = data.get('gender', details['gender'])
    if gender not in ['F', 'M', 'X']:
        return jsonify({"error": "Invalid gender value"}), 400

    age = data.get('age', details['age'])
    height = data.get('height', details['height'])
    weight = data.get('weight', details['weight'])
    kcal_goal = data.get('kcal_goal', details['kcal_goal'])
    fat_goal = data.get('fat_goal', details['fat_goal'])
    protein_goal = data.get('protein_goal', details['protein_goal'])
    carb_goal = data.get('carb_goal', details['carb_goal'])

    if any(value < 0 for value in [age, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal]):
        return jsonify({"error": "Age, height, weight, and goals must be greater than or equal to 0"}), 400

    cursor.execute('''
        UPDATE user_details
        SET age = %s, gender = %s, height = %s, weight = %s, kcal_goal = %s, fat_goal = %s, protein_goal = %s, carb_goal = %s
        WHERE user_id = %s
    ''', (age, gender, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User details updated successfully"}), 200

@login_required
def get_user_details(user_id):
    """
    Get user details
    ---
    tags:
      - User Details
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve details for
    responses:
      200:
        description: User details retrieved successfully
        schema:
          type: object
          properties:
            user_id:
              type: integer
            age:
              type: integer
            gender:
              type: string
            height:
              type: number
            weight:
              type: number
            kcal_goal:
              type: integer
            fat_goal:
              type: integer
            protein_goal:
              type: integer
            carb_goal:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: User or user details not found
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
    verifivation = verify_identity(user_id, 'You can only update details for yourself')
    if verifivation is not None:
        return verifivation

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT id FROM "user" WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User not found"}), 404

    cursor.execute('SELECT * FROM user_details WHERE user_id = %s', (user_id,))
    details = cursor.fetchone()
    cursor.close()
    conn.close()

    if details:
        return jsonify(details)
    else:
        return jsonify({"message": "User details not specified"}), 404