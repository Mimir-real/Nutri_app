from datetime import datetime
import psycopg2
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Tworzenie linków
    cursor.execute('SELECT * FROM link_types WHERE type = %s', ('activate',))
    link_type_activate = cursor.fetchone()
    cursor.execute('SELECT * FROM link_types WHERE type = %s', ('restore',))
    link_type_restore = cursor.fetchone()

    if not link_type_activate:
        print("Creating link type 'activate'")
        cursor.execute('INSERT INTO link_types (type) VALUES (%s)', ('activate',))
    if not link_type_restore:
        print("Creating link type 'restore'")
        cursor.execute('INSERT INTO link_types (type) VALUES (%s)', ('restore',))
    conn.commit()

    # Tworzenie diet
    cursor.execute('SELECT * FROM diet WHERE name = %s', ('Normal',))
    diet_normal = cursor.fetchone()
    cursor.execute('SELECT * FROM diet WHERE name = %s', ('Keto',))
    diet_keto = cursor.fetchone()
    cursor.execute('SELECT * FROM diet WHERE name = %s', ('Vegan',))
    diet_vegan = cursor.fetchone()

    if not diet_normal:
        print("Creating diet 'Normal'")
        cursor.execute('INSERT INTO diet (name, description) VALUES (%s, %s)', ('Normal', 'Balanced diet.'))
    if not diet_keto:
        print("Creating diet 'Keto'")
        cursor.execute('INSERT INTO diet (name, description) VALUES (%s, %s)', ('Keto', 'Low-carb, high-fat diet.'))
    if not diet_vegan:
        print("Creating diet 'Vegan'")
        cursor.execute('INSERT INTO diet (name, description) VALUES (%s, %s)', ('Vegan', 'Plant-based diet without animal products.'))
    conn.commit()

    # Tworzenie kategorii posiłków
    cursor.execute('SELECT * FROM meal_category WHERE category = %s', ('Breakfast',))
    category_breakfast = cursor.fetchone()
    if not category_breakfast:
        print("Creating meal category 'Breakfast'")
        cursor.execute('INSERT INTO meal_category (category, description) VALUES (%s, %s)', ('Breakfast', 'Morning meal'))

    cursor.execute('SELECT * FROM meal_category WHERE category = %s', ('Lunch',))
    category_lunch = cursor.fetchone()
    if not category_lunch:
        print("Creating meal category 'Lunch'")
        cursor.execute('INSERT INTO meal_category (category, description) VALUES (%s, %s)', ('Lunch', 'Midday meal'))

    cursor.execute('SELECT * FROM meal_category WHERE category = %s', ('Dinner',))
    category_dinner = cursor.fetchone()
    if not category_dinner:
        print("Creating meal category 'Dinner'")
        cursor.execute('INSERT INTO meal_category (category, description) VALUES (%s, %s)', ('Dinner', 'Evening meal'))

    cursor.execute('SELECT * FROM meal_category WHERE category = %s', ('Snack',))
    category_snack = cursor.fetchone()
    if not category_snack:
        print("Creating meal category 'Snack'")
        cursor.execute('INSERT INTO meal_category (category, description) VALUES (%s, %s)', ('Snack', 'Between meals'))

    conn.commit()
    cursor.close()
    conn.close()

    print("Database seeded successfully.")