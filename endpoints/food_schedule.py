from flask import request, jsonify
from models import db, FoodSchedule, Meal
from sqlalchemy import func

def create_food_schedule():
    pass

def get_food_schedules():
    pass


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