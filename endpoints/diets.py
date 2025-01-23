from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required

@login_required
def create_diet():
    """
    Create a new diet
    ---
    tags:
      - Diets
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
              description: The name of the diet
            description:
              type: string
              description: The description of the diet
    responses:
      201:
        description: Diet created
        schema:
          type: object
          properties:
            message:
              type: string
            diet_id:
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
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return jsonify({"error": "Name is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

def get_diets():
    """
    Get a list of diets
    ---
    tags:
      - Diets
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of diets to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
    responses:
      200:
        description: A list of diets
        schema:
          type: object
          properties:
            diets:
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
    try:
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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

def get_diet(diet_id):
    """
    Get a diet by ID
    ---
    tags:
      - Diets
    parameters:
      - in: path
        name: diet_id
        type: integer
        required: true
        description: The ID of the diet to retrieve
    responses:
      200:
        description: A diet object
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
      404:
        description: Diet not found
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

        cursor.execute('SELECT * FROM diet WHERE id = %s', (diet_id,))
        diet = cursor.fetchone()

        cursor.close()
        conn.close()

        if diet:
            return jsonify(diet)
        else:
            return jsonify({"message": "Diet not found"}), 404

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500