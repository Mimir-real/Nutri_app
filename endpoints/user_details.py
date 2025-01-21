from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection

@jwt_required()
def create_user_details(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

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

@jwt_required()
def update_user_details(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

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

@jwt_required()
def get_user_details(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

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