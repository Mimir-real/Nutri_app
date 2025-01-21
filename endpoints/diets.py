from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection

def create_diet():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO diet (name, description)
        VALUES (%s, %s)
        RETURNING id
    ''', (name, description))
    new_diet_id = cursor.fetchone()['id']

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Diet created", "diet_id": new_diet_id}), 201

def get_diets():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT COUNT(*) FROM diet')
    total = cursor.fetchone()['count']

    cursor.execute('''
        SELECT * FROM diet
        ORDER BY id
        LIMIT %s OFFSET %s
    ''', (limit, offset))
    diets = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "diets": diets,
        "total": total,
        "pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_page": page,
        "page_size": limit
    })

def get_diet(diet_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM diet WHERE id = %s', (diet_id,))
    diet = cursor.fetchone()

    cursor.close()
    conn.close()

    if diet:
        return jsonify(diet)
    else:
        return jsonify({"message": "Diet not specified"}), 404