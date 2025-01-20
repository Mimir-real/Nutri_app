def create_food_log():
    pass

def get_food_logs():
    pass


# # ==================== FOOD LOG CRUD ====================
# @app.route('/food_logs', methods=['POST'])
# def create_food_log():
#     data = request.get_json()
#     new_log = FoodLog(local_meal_id=data['local_meal_id'], portion=data['portion'], at=data['at'])
#     db.session.add(new_log)
#     db.session.commit()
#     return jsonify({"message": "Food log created", "food_log_id": new_log.id}), 201

# @app.route('/food_logs', methods=['GET'])
# def get_food_logs():
#     logs = FoodLog.query.all()
#     return jsonify([log.to_dict() for log in logs])
