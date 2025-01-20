from flask import request, jsonify
from models import db, Meal, MealCategory

def get_meal_categories():
    categories = MealCategory.query.all()
    return jsonify([category.to_dict() for category in categories])

def assign_category_to_meal(meal_id):
    data = request.get_json()
    if not data.get('category_id'):
        return jsonify({"error": "category_id is required"}), 400

    meal = Meal.query.get_or_404(meal_id)
    if meal.category_id is not None:
        return jsonify({"error": "Category is already assigned to this meal"}), 400

    category = MealCategory.query.get_or_404(data['category_id'])

    meal.version += 1
    meal.category_id = category.id
    db.session.commit()

    return jsonify({"message": "Category assigned to meal"}), 200

def remove_category_from_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    if meal.category_id is None:
        return jsonify({"error": "No category assigned to this meal"}), 400

    meal.category_id = None
    db.session.commit()

    return jsonify({"message": "Category removed from meal"}), 200

def update_category_of_meal(meal_id):
    data = request.get_json()
    if not data.get('category_id'):
        return jsonify({"error": "category_id is required"}), 400

    meal = Meal.query.get_or_404(meal_id)
    if meal.category_id is None:
        return jsonify({"error": "No category assigned to this meal"}), 400

    category = MealCategory.query.get_or_404(data['category_id'])

    meal.version += 1
    meal.category_id = category.id
    db.session.commit()

    return jsonify({"message": "Category updated for meal"}), 200