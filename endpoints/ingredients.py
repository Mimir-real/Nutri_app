from flask import request, jsonify
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required

@login_required
def get_ingredients():
    """
    Get a list of ingredients
    ---
    tags:
      - Ingredients
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of ingredients to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
    responses:
      200:
        description: A list of ingredients
        schema:
          type: object
          properties:
            ingredients:
              type: array
              items:
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
    """
    Get an ingredient by ID
    ---
    tags:
      - Ingredients
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ing_id
        type: integer
        required: true
        description: The ID of the ingredient to retrieve
    responses:
      200:
        description: An ingredient object
        schema:
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
      404:
        description: Ingredient not found
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
    """
    Search for ingredients
    ---
    tags:
      - Ingredients
    security:
      - Bearer: []
    parameters:
      - in: query
        name: query
        type: string
        description: The search query
        default: ''
      - in: query
        name: barcode
        type: string
        description: The barcode to search for
        default: ''
      - in: query
        name: top
        type: integer
        description: Number of top results to return
        default: 10
    responses:
      200:
        description: A list of search results
        schema:
          type: array
          items:
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
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    query = request.args.get('query', default='', type=str)
    barcode = request.args.get('barcode', default='', type=str)
    top = request.args.get('top', default=10, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if barcode:
        cursor.execute('''
            SELECT * FROM ingredients
            WHERE barcode = %s
            LIMIT %s
        ''', (barcode, top))
    else:
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