from flask import request, jsonify
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required

@login_required
def get_ingredients():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT COUNT(*) FROM ingredients')
    total = cursor.fetchone()['count']

    cursor.execute('''
        SELECT * FROM ingredients
        ORDER BY id
        LIMIT %s OFFSET %s
    ''', (limit, offset))
    ingredients = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "ingredients": ingredients,
        "total": total,
        "pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_page": page,
        "page_size": limit
    })

@login_required
def get_ingredient_by_id(ing_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM ingredients WHERE id = %s', (ing_id,))
    ingredient = cursor.fetchone()

    cursor.close()
    conn.close()

    if ingredient:
        return jsonify(ingredient)
    else:
        return jsonify({"message": "Ingredient not found"}), 404

@login_required
def search_ingredients():
    query = request.args.get('query', default='', type=str)
    top = request.args.get('top', default=10, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('''
        SELECT * FROM ingredients
        WHERE to_tsvector('english', product_name || ' ' || generic_name) @@ plainto_tsquery('english', %s)
        AND product_quantity IS NOT NULL
        LIMIT %s
    ''', (query, top))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(results)