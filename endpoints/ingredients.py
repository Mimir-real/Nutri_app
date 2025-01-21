from flask import request, jsonify
from models import db, Ingredients
from sqlalchemy import func

def get_ingredients():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    ingredients_pagination = Ingredients.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    ingredients = ingredients_pagination.items
    return jsonify({
        "ingredients": [ing.to_dict() for ing in ingredients],
        "total": ingredients_pagination.total,
        "pages": ingredients_pagination.pages,
        "current_page": ingredients_pagination.page,
        "page_size": ingredients_pagination.per_page
    })

def get_ingredient_by_id(ing_id):
    ingredient = Ingredients.query.get(ing_id)
    if ingredient:
        return jsonify(ingredient.to_dict())
    else:
        return jsonify({"message": "Ingredient not found"}), 404

def search_ingredients(query):
    top = request.args.get('top', default=10, type=int)
    
    # Use full-text search for better matching and filter out ingredients with null product_quantity
    results = Ingredients.query.filter(
        func.to_tsvector('english', Ingredients.product_name + ' ' + Ingredients.generic_name).match(query),
        Ingredients.product_quantity.isnot(None)
    ).limit(top).all()
    
    # Return all fields in the row
    return jsonify([{
        column.name: getattr(item, column.name)
        for column in Ingredients.__table__.columns
    } for item in results])