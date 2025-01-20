from flask import request, jsonify
from models import db, FoodSchedule, MealHistory, MealIngredients, Ingredients
from datetime import datetime, timedelta

def generate_shopping_list(user_id):
    days = request.args.get('days', default=7, type=int)
    if days < 1:
        return jsonify({"error": "Days must be a positive integer"}), 400

    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=days)

    # Pobierz zaplanowane posiłki dla użytkownika na X dni w przód
    food_schedules = FoodSchedule.query.filter(
        FoodSchedule.user_id == user_id,
        FoodSchedule.at >= start_date,
        FoodSchedule.at < end_date
    ).all()

    meals = []
    ingredients_summary = {}

    for schedule in food_schedules:
        meal_history = MealHistory.query.get(schedule.meal_history_id)
        if not meal_history:
            continue

        meal = meal_history.composition
        meal_ingredients = MealIngredients.query.filter_by(meal_id=meal['id']).all()

        meal_details = {
            "meal": meal,
            "ingredients": []
        }

        for meal_ingredient in meal_ingredients:
            ingredient = Ingredients.query.get(meal_ingredient.ingredient_id)
            if not ingredient:
                continue

            ingredient_details = {
                "ingredient": ingredient.to_dict(),
                "quantity": meal_ingredient.quantity,
                "unit": meal_ingredient.unit
            }
            meal_details["ingredients"].append(ingredient_details)

            # Dodaj do zbiorczej listy produktów
            if ingredient.id not in ingredients_summary:
                ingredients_summary[ingredient.id] = {
                    "ingredient": ingredient.to_dict(),
                    "total_quantity": 0,
                    "unit": meal_ingredient.unit
                }
            ingredients_summary[ingredient.id]["total_quantity"] += meal_ingredient.quantity

        meals.append(meal_details)

    # Konwertuj zbiorczą listę produktów do formatu listy
    ingredients_summary_list = [
        {
            "ingredient": details["ingredient"],
            "total_quantity": details["total_quantity"],
            "unit": details["unit"]
        }
        for details in ingredients_summary.values()
    ]

    return jsonify({
        "meals": meals,
        "ingredients_summary": ingredients_summary_list
    })