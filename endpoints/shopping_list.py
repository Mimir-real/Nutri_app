from flask import request, jsonify
from datetime import datetime, timedelta
from db_config import get_db_connection

def generate_shopping_list(user_id):
    days = request.args.get('days', default=7, type=int)
    if days < 1:
        return jsonify({"error": "Days must be a positive integer"}), 400

    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=days)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Pobierz zaplanowane posiłki dla użytkownika na X dni w przód
    cursor.execute('''
        SELECT fs.meal_history_id
        FROM food_schedule fs
        WHERE fs.user_id = %s AND fs.at >= %s AND fs.at < %s
    ''', (user_id, start_date, end_date))
    food_schedules = cursor.fetchall()

    meals = []
    ingredients_summary = {}

    for schedule in food_schedules:
        meal_history_id = schedule[0]
        cursor.execute('SELECT composition FROM meal_history WHERE id = %s', (meal_history_id,))
        meal_history = cursor.fetchone()
        if not meal_history:
            continue

        composition = meal_history[0]
        meal = composition['meal']
        meal_ingredients = composition['ingredients']

        meal_details = {
            "meal": meal,
            "ingredients": []
        }

        for meal_ingredient in meal_ingredients:
            ingredient_id = meal_ingredient['ingredient_id']
            cursor.execute('SELECT * FROM ingredients WHERE id = %s', (ingredient_id,))
            ingredient = cursor.fetchone()
            if not ingredient:
                continue

            ingredient_details = {
                "ingredient": {
                    "id": ingredient[0],
                    "product_name": ingredient[1],
                    "generic_name": ingredient[2],
                    "kcal_100g": ingredient[3],
                    "protein_100g": ingredient[4],
                    "carbs_100g": ingredient[5],
                    "fat_100g": ingredient[6],
                    "brand": ingredient[7],
                    "barcode": ingredient[8],
                    "image_url": ingredient[9],
                    "labels_tags": ingredient[10],
                    "product_quantity": ingredient[11],
                    "allergens": ingredient[12],
                    "tsv": ingredient[13]
                },
                "quantity": meal_ingredient['quantity'],
                "unit": meal_ingredient['unit']
            }
            meal_details["ingredients"].append(ingredient_details)

            # Dodaj do zbiorczej listy produktów
            if ingredient[0] not in ingredients_summary:
                ingredients_summary[ingredient[0]] = {
                    "ingredient": ingredient_details["ingredient"],
                    "total_quantity": 0,
                    "unit": meal_ingredient['unit']
                }
            ingredients_summary[ingredient[0]]["total_quantity"] += meal_ingredient['quantity']

        meals.append(meal_details)

    cursor.close()
    conn.close()

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