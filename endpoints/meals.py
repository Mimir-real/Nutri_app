from flask import request, jsonify
from models import db, Meal, MealCategory, Diet, MealIngredients, MealHistory, UserDiets
from datetime import datetime
from sqlalchemy import or_

def get_meals():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    meals_pagination = Meal.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    meals = meals_pagination.items
    return jsonify({
        "meals": [meal.to_dict() for meal in meals],
        "total": meals_pagination.total,
        "pages": meals_pagination.pages,
        "current_page": meals_pagination.page,
        "page_size": meals_pagination.per_page
    })

def get_meal(meal_id):
    meal = Meal.query.get(meal_id)
    if meal:
        return jsonify(meal.to_dict())
    else:
        return jsonify({"message": "Meal not found"}), 404

def search_meals():
    query = request.args.get('query', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    user_id = request.args.get('user_id', default=None, type=int)
    allow_more = request.args.get('allowMore', default=False, type=bool)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    # Podstawowe filtrowanie na podstawie nazwy i opisu posiłku
    filters = [or_(Meal.name.ilike(f'%{query}%'), Meal.description.ilike(f'%{query}%'))]

    # Jeśli podano user_id, dodaj filtrowanie na podstawie dozwolonych i zabronionych diet
    if user_id:
        allowed_diets = db.session.query(UserDiets.diet_id).filter_by(user_id=user_id, allowed=True).subquery()
        forbidden_diets = db.session.query(UserDiets.diet_id).filter_by(user_id=user_id, allowed=False).subquery()

        if allow_more:
            filters.append(~Meal.diet_id.in_(forbidden_diets))
        else:
            filters.append(Meal.diet_id.in_(allowed_diets))
            filters.append(~Meal.diet_id.in_(forbidden_diets))

    meals_pagination = Meal.query.filter(*filters).paginate(page=page, per_page=limit, max_per_page=100, error_out=False)

    meals = meals_pagination.items
    return jsonify({
        "meals": [meal.to_dict() for meal in meals],
        "total": meals_pagination.total,
        "pages": meals_pagination.pages,
        "current_page": meals_pagination.page,
        "page_size": meals_pagination.per_page
    })

# Tworzenie, aktualizacja i usuwanie posiłków
def create_meal():
    data = request.get_json()

    if not data.get('name') or not data.get('creator_id'):
        return jsonify({"error": "Name and creator_id are required"}), 400
    
    # Zakładamy że w sesji jest zapisane user_id (creator_id)
    # My bierzemy je z body dla celów prezentacyjnych
    creator_id = data.get('creator_id')

    category_id = data.get('category_id')
    if category_id:
        category = MealCategory.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

    diet_id = data.get('diet_id')
    if diet_id:
        diet = Diet.query.get(diet_id)
        if not diet:
            return jsonify({"error": "Diet not found"}), 404

    # Create new meal
    new_meal = Meal(
        name=data.get('name'),
        description=data.get('description', ""),
        creator_id=creator_id,
        diet_id=diet_id,
        category_id=category_id,
        version=1,
        last_update=datetime.utcnow()
    )
    db.session.add(new_meal)
    db.session.commit()

    ingredients = data.get('ingredients', [])
    for ingredient in ingredients:
        meal_ingredient = MealIngredients(
            meal_id=new_meal.id,
            ingredient_id=ingredient['ingredient_id'],
            unit=ingredient['unit'],
            quantity=ingredient['quantity']
        )
        db.session.add(meal_ingredient)
    db.session.commit()

    new_meal.save_meal_version()
    db.session.commit()
    return jsonify({"message": "Meal created", "meal_id": new_meal.id}), 201

# Aktualizacja danych posiłku, ale bez zmiany składników
def update_meal(meal_id):
    data = request.get_json()
    
    if data.get('ingredients'):
        return jsonify({"error": "To update ingredients, use the /meals/<meal_id>/ingredients endpoint"}), 400

    meal = Meal.query.get(meal_id)
    if not meal:
        return jsonify({"message": "Meal not found"}), 404
    meal.save_meal_version()

    # Update meal details
    meal.name = data.get('name', meal.name)
    meal.description = data.get('description', meal.description)
    meal.diet_id = data.get('diet_id', meal.diet_id)
    meal.category_id = data.get('category_id', meal.category_id)
    meal.version += 1
    meal.last_update = datetime.utcnow()
    db.session.commit()

    # Save new version to MealHistory
    meal.save_meal_version()
    db.session.commit()
    return jsonify({"message": "Meal updated", "meal_id": meal.id}), 200

def delete_meal(meal_id):
    meal = Meal.query.get(meal_id)
    if not meal:
        return jsonify({"message": "Meal not found"}), 404
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Meal deleted"})

def get_meal_versions(meal_id):
    meal_versions = MealHistory.query.filter_by(meal_id=meal_id).all()
    return jsonify({
        "meal_versions": [meal_version.to_dict() for meal_version in meal_versions]
    })