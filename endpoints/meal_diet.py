from flask import request, jsonify
from models import db, Meal, Diet

def assign_diet_to_meal(meal_id):
    data = request.get_json()
    if not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400

    meal = Meal.query.get_or_404(meal_id)
    if meal.diet_id is not None:
        return jsonify({"error": "Diet is already assigned to this meal"}), 400

    diet = Diet.query.get_or_404(data['diet_id'])

    meal.version += 1
    meal.diet_id = diet.id
    db.session.commit()

    return jsonify({"message": "Diet assigned to meal"}), 200

def remove_diet_from_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    if meal.diet_id is None:
        return jsonify({"error": "No diet assigned to this meal"}), 400

    meal.version += 1
    meal.diet_id = None
    db.session.commit()

    return jsonify({"message": "Diet removed from meal"}), 200

def update_diet_of_meal(meal_id):
    data = request.get_json()
    if not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400

    meal = Meal.query.get_or_404(meal_id)
    if meal.diet_id is None:
        return jsonify({"error": "No diet assigned to this meal"}), 400

    diet = Diet.query.get_or_404(data['diet_id'])

    meal.version += 1
    meal.diet_id = diet.id
    db.session.commit()

    return jsonify({"message": "Diet updated for meal"}), 200