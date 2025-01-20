from flask import request, jsonify
from models import db, FoodSchedule, MealHistory
from datetime import datetime

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

# # ==================== FOOD SCHEDULE CRUD ====================
# @app.route('/food_schedules', methods=['POST'])
# def create_food_schedule():
#     data = request.get_json()
#     new_schedule = FoodSchedule(local_meal_id=data['local_meal_id'], at=data['at'])
#     db.session.add(new_schedule)
#     db.session.commit()
#     return jsonify({"message": "Food schedule created", "schedule_id": new_schedule.id}), 201

# @app.route('/food_schedules', methods=['GET'])
# def get_food_schedules():
#     schedules = FoodSchedule.query.all()
#     return jsonify([s.to_dict() for s in schedules])