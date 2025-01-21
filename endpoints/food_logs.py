from flask import request, jsonify
from models import db, FoodLog, MealHistory
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

# Pobieranie wszystkich logów posiłków
def get_food_logs():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    food_logs_pagination = FoodLog.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    food_logs = food_logs_pagination.items

    return jsonify({
        "food_logs": [fl.to_dict() for fl in food_logs],
        "total": food_logs_pagination.total,
        "pages": food_logs_pagination.pages,
        "current_page": food_logs_pagination.page,
        "page_size": food_logs_pagination.per_page
    })

# Pobieranie logu posiłku według ID
def get_food_log(food_log_id):
    food_log = FoodLog.query.get(food_log_id)
    if food_log:
        return jsonify(food_log.to_dict())
    else:
        return jsonify({"message": "Food log not found"}), 404

# Tworzenie nowego logu posiłku
def create_food_log():
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('meal_id') or not data.get('meal_version') or not data.get('portion') or not data.get('at') or not data.get('user_id'):
            return jsonify({"error": "meal_id, meal_version, portion, at, and user_id are required"}), 400

        # Validate meal_id and meal_version
        meal_history = MealHistory.query.filter_by(meal_id=data['meal_id'], meal_version=data['meal_version']).first()
        if not meal_history:
            return jsonify({"error": "Meal history not found for the given ID and version"}), 404

        # Parse the 'at' field
        try:
            at_time = datetime.strptime(data['at'], '%H:%M:%S %d-%m-%Y')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use 'HH:MM:SS DD-MM-YYYY'"}), 400

        # Create new food log
        new_food_log = FoodLog(
            meal_history_id=meal_history.id,
            portion=data['portion'],  # Portion in grams
            at=at_time,
            user_id=data['user_id']
        )
        db.session.add(new_food_log)
        db.session.commit()

        return jsonify({"message": "Food log created", "food_log_id": new_food_log.id}), 201

    except IntegrityError as e:
        print('POST /food/logs - IntegrityError:', e)
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        print('POST /food/logs - Exception:', e)
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

# Usuwanie logu posiłku
def delete_food_log(food_log_id):
    food_log = FoodLog.query.get(food_log_id)
    if food_log:
        db.session.delete(food_log)
        db.session.commit()
        return jsonify({"message": "Food log deleted"})
    else:
        return jsonify({"message": "Food log not found"}), 404

# Przeliczanie dziennego spożycia kalorii i makroskładników
def calculate_daily_nutrients(user_id, date):
    start_date = datetime.strptime(date, '%d-%m-%Y')
    end_date = start_date + timedelta(days=1)

    food_logs = FoodLog.query.filter(
        FoodLog.user_id == user_id,
        FoodLog.at >= start_date,
        FoodLog.at < end_date
    ).all()

    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    for log in food_logs:
        meal_history = MealHistory.query.get(log.meal_history_id)
        if meal_history:
            nutrients = meal_history.calculate_nutrients()
            total_weight = meal_history.calculate_total_weight()
            total_calories += (nutrients['calories'] / total_weight) * log.portion
            total_protein += (nutrients['protein'] / total_weight) * log.portion
            total_carbs += (nutrients['carbs'] / total_weight) * log.portion
            total_fat += (nutrients['fat'] / total_weight) * log.portion

    return jsonify({
        "date": date,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat
    })

# Pobieranie logów posiłków dla danego użytkownika z danego dnia
def get_food_logs_by_date(user_id, date):
    try:
        start_date = datetime.strptime(date, '%d-%m-%Y')
        end_date = start_date + timedelta(days=1)

        food_logs = FoodLog.query.filter(
            FoodLog.user_id == user_id,
            FoodLog.at >= start_date,
            FoodLog.at < end_date
        ).all()

        result = []
        for log in food_logs:
            meal_history = MealHistory.query.get(log.meal_history_id)
            if meal_history:
                log_details = log.to_dict()
                log_details['meal'] = meal_history.composition['meal']
                result.append(log_details)

        return jsonify(result)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'DD-MM-YYYY'"}), 400

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500