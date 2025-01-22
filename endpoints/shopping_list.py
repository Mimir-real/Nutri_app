from flask import request, jsonify
from datetime import datetime, timedelta
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor
from endpoints.auth import login_required, verify_identity

@login_required
def generate_shopping_list(user_id):
    verifivation = verify_identity(user_id, 'You can only generate shopping list for yourself')
    if verifivation is not None:
        return verifivation

    try:
        days = request.args.get('days', default=7, type=int)
        if days < 1:
            return jsonify({"error": "Days must be a positive integer"}), 400

        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=days)

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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
            meal_history_id = schedule['meal_history_id']
            cursor.execute('SELECT composition FROM meal_history WHERE id = %s', (meal_history_id,))
            meal_history = cursor.fetchone()
            if not meal_history:
                continue

            composition = meal_history['composition']
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
                        "id": ingredient['id'],
                        "product_name": ingredient['product_name'],
                        "generic_name": ingredient['generic_name'],
                        "kcal_100g": ingredient['kcal_100g'],
                        "protein_100g": ingredient['protein_100g'],
                        "carbs_100g": ingredient['carbs_100g'],
                        "fat_100g": ingredient['fat_100g'],
                        "brand": ingredient['brand'],
                        "barcode": ingredient['barcode'],
                        "image_url": ingredient['image_url'],
                        "labels_tags": ingredient['labels_tags'],
                        "product_quantity": ingredient['product_quantity'],
                        "allergens": ingredient['allergens'],
                        "tsv": ingredient['tsv']
                    },
                    "quantity": meal_ingredient['quantity'],
                    "unit": meal_ingredient['unit']
                }
                meal_details["ingredients"].append(ingredient_details)

                # Dodaj do zbiorczej listy produktów
                if ingredient['id'] not in ingredients_summary:
                    ingredients_summary[ingredient['id']] = {
                        "ingredient": ingredient_details["ingredient"],
                        "total_quantity": 0,
                        "unit": meal_ingredient['unit']
                    }
                ingredients_summary[ingredient['id']]["total_quantity"] += meal_ingredient['quantity']

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

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500