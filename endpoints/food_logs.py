from flask import request, jsonify
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity
from flask_jwt_extended import get_jwt_identity

# Pobieranie wszystkich logów posiłków
@login_required
def get_food_logs():
    try:
        limit = request.args.get('limit', default=10, type=int)
        page = request.args.get('page', default=1, type=int)

        if limit < 1 or page < 1:
            return jsonify({"error": "Limit and page must be positive integers"}), 400

        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT COUNT(*) FROM food_log')
        total = cursor.fetchone()['count']

        cursor.execute('''
            SELECT * FROM food_log
            ORDER BY id
            LIMIT %s OFFSET %s
        ''', (limit, offset))
        food_logs = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "food_logs": food_logs,
            "total": total,
            "pages": (total // limit) + (1 if total % limit > 0 else 0),
            "current_page": page,
            "page_size": limit
        })
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Pobieranie logu posiłku według ID
@login_required
def get_food_log(food_log_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_log WHERE id = %s', (food_log_id,))
        food_log = cursor.fetchone()

        cursor.close()
        conn.close()

        if food_log:
            return jsonify(food_log)
        else:
            return jsonify({"message": "Food log not found"}), 404
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Tworzenie nowego logu posiłku
@login_required
def create_food_log():
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('meal_id') or not data.get('meal_version') or not data.get('portion') or not data.get('at'):
            return jsonify({"error": "meal_id, meal_version, portion, at, and user_id are required"}), 400

        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Validate meal_id and meal_version
        cursor.execute('SELECT * FROM meal_history WHERE meal_id = %s AND meal_version = %s', (data['meal_id'], data['meal_version']))
        meal_history = cursor.fetchone()
        if not meal_history:
            cursor.close()
            conn.close()
            return jsonify({"error": "Meal history not found for the given ID and version"}), 404

        # Parse the 'at' field
        try:
            at_time = datetime.strptime(data['at'], '%H:%M:%S %d-%m-%Y')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use 'HH:MM:SS DD-MM-YYYY'"}), 400

        # Create new food log
        cursor.execute('''
            INSERT INTO food_log (meal_history_id, portion, at, user_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (meal_history['id'], data['portion'], at_time, user_id))
        new_food_log_id = cursor.fetchone()['id']

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Food log created", "food_log_id": new_food_log_id}), 201

    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

# Usuwanie logu posiłku
@login_required
def delete_food_log(food_log_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_log WHERE id = %s', (food_log_id,))
        food_log = cursor.fetchone()

        if not food_log:
            cursor.close()
            conn.close()
            return jsonify({"message": "Food log not found"}), 404

        food_log_user_id = food_log['user_id']
        verifivation = verify_identity(food_log_user_id, 'You can only delete your own food logs')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        cursor.execute('DELETE FROM food_log WHERE id = %s', (food_log_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Food log deleted"})
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Przeliczanie dziennego spożycia kalorii i makroskładników
@login_required
def calculate_daily_nutrients(user_id, date):
    verifivation = verify_identity(user_id, 'You can only calculate nutrients for your own account')
    if verifivation is not None:
        return verifivation

    try:
        start_date = datetime.strptime(date, '%d-%m-%Y')
        end_date = start_date + timedelta(days=1)

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('''
            SELECT * FROM food_log
            WHERE user_id = %s AND at >= %s AND at < %s
        ''', (user_id, start_date, end_date))
        food_logs = cursor.fetchall()

        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for log in food_logs:
            cursor.execute('SELECT composition FROM meal_history WHERE id = %s', (log['meal_history_id'],))
            meal_history = cursor.fetchone()
            if meal_history:
                composition = meal_history['composition']
                ingredients = composition['ingredients']
                total_weight = sum(ingredient['quantity'] for ingredient in ingredients)
                for ingredient in ingredients:
                    cursor.execute('SELECT * FROM ingredients WHERE id = %s', (ingredient['ingredient_id'],))
                    ingredient_details = cursor.fetchone()
                    if ingredient_details:
                        if ingredient_details['kcal_100g']:
                            total_calories += (ingredient['quantity'] * ingredient_details['kcal_100g']) / 100
                        if ingredient_details['protein_100g']:
                            total_protein += (ingredient['quantity'] * ingredient_details['protein_100g']) / 100
                        if ingredient_details['carbs_100g']:
                            total_carbs += (ingredient['quantity'] * ingredient_details['carbs_100g']) / 100
                        if ingredient_details['fat_100g']:
                            total_fat += (ingredient['quantity'] * ingredient_details['fat_100g']) / 100

        response = {
            "date": date,
            "nutrients": {
                "total_kcal": total_calories,
                "total_protein": total_protein,
                "total_carbs": total_carbs,
                "total_fat": total_fat
            }
        }

        compare_details = request.args.get('compareDetails', 'false').lower() == 'true'
        if compare_details:
            cursor.execute('SELECT * FROM user_details WHERE user_id = %s', (user_id,))
            user_details = cursor.fetchone()
            if user_details:
                response["details"] = {
                    "kcal_goal": user_details['kcal_goal'],
                    "fat_goal": user_details['fat_goal'],
                    "protein_goal": user_details['protein_goal'],
                    "carb_goal": user_details['carb_goal']
                }
                response["percentage"] = {
                    "kcal_percentage": (total_calories / user_details['kcal_goal']) * 100 if user_details['kcal_goal'] else 0,
                    "fat_percentage": (total_fat / user_details['fat_goal']) * 100 if user_details['fat_goal'] else 0,
                    "protein_percentage": (total_protein / user_details['protein_goal']) * 100 if user_details['protein_goal'] else 0,
                    "carbs_percentage": (total_carbs / user_details['carb_goal']) * 100 if user_details['carb_goal'] else 0
                }

        cursor.close()
        conn.close()

        return jsonify(response)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'DD-MM-YYYY'"}), 400
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Pobieranie logów posiłków dla danego użytkownika z danego dnia
@login_required
def get_food_logs_by_date_for_user(user_id, date):
    verifivation = verify_identity(user_id, 'You can only calculate nutrients for your own account')
    if verifivation is not None:
        return verifivation

    try:
        start_date = datetime.strptime(date, '%d-%m-%Y')
        end_date = start_date + timedelta(days=1)

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('''
            SELECT * FROM food_log
            WHERE user_id = %s AND at >= %s AND at < %s
        ''', (user_id, start_date, end_date))
        food_logs = cursor.fetchall()

        result = []
        for log in food_logs:
            cursor.execute('SELECT composition FROM meal_history WHERE id = %s', (log['meal_history_id'],))
            meal_history = cursor.fetchone()
            if meal_history:
                log_details = dict(log)
                log_details['meal'] = meal_history['composition']['meal']
                result.append(log_details)

        cursor.close()
        conn.close()

        return jsonify(result)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'DD-MM-YYYY'"}), 400
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@login_required
def get_food_logs_for_user(user_id):
    verifivation = verify_identity(user_id, 'You can only calculate nutrients for your own account')
    if verifivation is not None:
        return verifivation
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_log WHERE user_id = %s', (user_id,))
        food_logs = cursor.fetchall()

        result = []
        for log in food_logs:
            cursor.execute('SELECT composition FROM meal_history WHERE id = %s', (log['meal_history_id'],))
            meal_history = cursor.fetchone()
            if meal_history:
                log_details = dict(log)
                log_details['meal'] = meal_history['composition']['meal']
                result.append(log_details)

        cursor.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500