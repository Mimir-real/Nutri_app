import json
from datetime import datetime

def create_meal_history(cursor, meal_id):
    cursor.execute('SELECT diet_id, category_id, last_update, version FROM meal WHERE id = %s', (meal_id,))
    updated_meal = cursor.fetchone()

    # Konwertuj last_update na string
    if updated_meal['last_update'] is not None:
        updated_meal['last_update'] = updated_meal['last_update'].isoformat()

    cursor.execute('SELECT ingredient_id, unit, quantity FROM meal_ingredients WHERE meal_id = %s', (meal_id,))
    updated_ingredients = cursor.fetchall()

    composition = {
        "meal": updated_meal,
        "ingredients": updated_ingredients
    }

    cursor.execute('''
        INSERT INTO meal_history (meal_id, meal_version, composition)
        VALUES (%s, %s, %s)
    ''', (meal_id, updated_meal['version'], json.dumps(composition)))