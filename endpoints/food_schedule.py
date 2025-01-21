from flask import request, jsonify
from models import db, FoodSchedule, MealHistory
from datetime import datetime, timedelta

# Pobieranie wszystkich harmonogramów posiłków
def get_food_schedules():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    food_schedules_pagination = FoodSchedule.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    food_schedules = food_schedules_pagination.items

    return jsonify({
        "food_schedules": [fs.to_dict() for fs in food_schedules],
        "total": food_schedules_pagination.total,
        "pages": food_schedules_pagination.pages,
        "current_page": food_schedules_pagination.page,
        "page_size": food_schedules_pagination.per_page
    })

# Pobieranie harmonogramu posiłków według ID
def get_food_schedule(schedule_id):
    food_schedule = FoodSchedule.query.get_or_404(schedule_id)
    return jsonify(food_schedule.to_dict())

def create_food_schedule():
    data = request.get_json()

    # Validate required fields
    if not data.get('meal_id') or not data.get('meal_version') or not data.get('at') or not data.get('user_id'):
        return jsonify({"error": "meal_id, meal_version, at, and user_id are required"}), 400

    # Validate meal_id and meal_version
    meal_history = MealHistory.query.filter_by(meal_id=data['meal_id'], meal_version=data['meal_version']).first()
    if not meal_history:
        return jsonify({"error": "Meal history not found for the given ID and version"}), 404

    # Validate 'at' is greater than current time
    at_time = datetime.strptime(data['at'], '%H:%M:%S %d-%m-%Y')
    if at_time <= datetime.utcnow():
        return jsonify({"error": "'at' must be a future time"}), 400

    # Create new food schedule
    new_food_schedule = FoodSchedule(
        meal_history_id=meal_history.id,
        at=at_time,  # Kiedy użytkownik ma zjeść posiłek
        user_id=data['user_id']
    )
    db.session.add(new_food_schedule)
    db.session.commit()

    return jsonify({"message": "Food schedule created", "food_schedule_id": new_food_schedule.id}), 201

# Usuwanie harmonogramu posiłków
def delete_food_schedule(schedule_id):
    food_schedule = FoodSchedule.query.get_or_404(schedule_id)
    db.session.delete(food_schedule)
    db.session.commit()
    return jsonify({"message": "Food schedule deleted"})

# Pobieranie zaplanowanych posiłków dla danego użytkownika z danego dnia
def get_food_schedule_by_date(user_id, date):
    try:
        start_date = datetime.strptime(date, '%d-%m-%Y')
        end_date = start_date + timedelta(days=1)

        food_schedules = FoodSchedule.query.filter(
            FoodSchedule.user_id == user_id,
            FoodSchedule.at >= start_date,
            FoodSchedule.at < end_date
        ).all()

        result = []
        for schedule in food_schedules:
            meal_history = MealHistory.query.get(schedule.meal_history_id)
            if meal_history:
                schedule_details = schedule.to_dict()
                schedule_details['meal'] = meal_history.composition['meal']
                result.append(schedule_details)

        return jsonify(result)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'DD-MM-YYYY'"}), 400

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500