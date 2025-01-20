from flask import request, jsonify
from models import db, Meal, MealIngredients, Ingredients
from sqlalchemy.exc import IntegrityError

def get_meal_ingredients(meal_id):
    # Fetch meal ingredients with actual ingredient details
    results = db.session.query(MealIngredients, Ingredients).join(Ingredients, MealIngredients.ingredient_id == Ingredients.id).filter(MealIngredients.meal_id == meal_id).all()

    # Map the results to a list of dictionaries
    ingredients = []
    for meal_ingredient, ingredient in results:
        ingredient_dict = {
            'ingredient': ingredient.to_dict(),
            'details': meal_ingredient.to_dict()
        }
        ingredients.append(ingredient_dict)

    return jsonify(ingredients)

# Zastępowanie całej listy składników posiłku
def replace_meal_ingredients(meal_id):
    data = request.get_json()

    if data.get('ingredients') is None:
        return jsonify({"error": "Ingredients list is required"}), 400
    ingredients = data['ingredients']

    # Usuń istniejące składniki posiłku
    MealIngredients.query.filter_by(meal_id=meal_id).delete()

    # Dodaj nowe składniki
    for ingredient_data in ingredients:
        ingredient = MealIngredients(
            meal_id=meal_id,
            ingredient_id=ingredient_data['ingredient_id'],
            unit=ingredient_data['unit'],
            quantity=ingredient_data['quantity']
        )
        db.session.add(ingredient)

    # Zaktualizuj wersję posiłku
    meal = Meal.query.get_or_404(meal_id)
    meal.version += 1

    db.session.commit()
    return jsonify({"message": "Meal ingredients updated successfully"}), 200

# Dodawanie nowego składnika do posiłku
def add_meal_ingredient(meal_id):
    data = request.get_json()
    
    if not data.get('ingredient_id') or not data.get('unit') or not data.get('quantity'):
        return jsonify({"error": "ingredient_id, unit, and quantity are required"}), 400

    ingredient = MealIngredients(
        meal_id=meal_id,
        ingredient_id=data['ingredient_id'],
        unit=data['unit'],
        quantity=data['quantity']
    )
    db.session.add(ingredient)

    try:
        meal = Meal.query.get_or_404(meal_id)
        meal.version += 1

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This ingredient is already assigned to the meal"}), 400

    return jsonify({"message": "Ingredient added successfully"}), 201

# Usuwanie składnika z posiłku
def remove_meal_ingredient(meal_id, ingredient_id):
    ingredient = MealIngredients.query.filter_by(meal_id=meal_id, ingredient_id=ingredient_id).first()
    if not ingredient:
        return jsonify({"error": "Ingredient not found in meal"}), 404

    db.session.delete(ingredient)

    try:
        # Zaktualizuj wersję posiłku
        meal = Meal.query.get_or_404(meal_id)
        meal.version += 1

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to remove ingredient"}), 400

    return jsonify({"message": "Ingredient removed successfully"}), 200