from flask import request, jsonify
from models import db, UserDetails

def create_user_details(user_id):
    data = request.get_json()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    details = UserDetails.query.get(user_id)
    if details:
        return jsonify({"error": "User details already exist"}), 400

    gender = data.get('gender', 'X')
    if gender not in ['F', 'M', 'X']:
        return jsonify({"error": "Invalid gender value"}), 400

    age = data.get('age', 0)
    height = data.get('height', 0.0)
    weight = data.get('weight', 0.0)
    kcal_goal = data.get('kcal_goal', 0)
    fat_goal = data.get('fat_goal', 0)
    protein_goal = data.get('protein_goal', 0)
    carb_goal = data.get('carb_goal', 0)

    if any(value < 0 for value in [age, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal]):
        return jsonify({"error": "Age, height, weight, and goals must be greater than or equal to 0"}), 400

    # Create new UserDetails
    details = UserDetails(
        user_id=user_id,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        kcal_goal=kcal_goal,
        fat_goal=fat_goal,
        protein_goal=protein_goal,
        carb_goal=carb_goal
    )
    db.session.add(details)
    db.session.commit()
    return jsonify({"message": "User details created successfully"}), 201

def update_user_details(user_id):
    data = request.get_json()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    details = UserDetails.query.get(user_id)
    if not details:
        return jsonify({"message": "User details not found"}), 404

    gender = data.get('gender', details.gender)
    if gender not in ['F', 'M', 'X']:
        return jsonify({"error": "Invalid gender value"}), 400

    age = data.get('age', details.age)
    height = data.get('height', details.height)
    weight = data.get('weight', details.weight)
    kcal_goal = data.get('kcal_goal', details.kcal_goal)
    fat_goal = data.get('fat_goal', details.fat_goal)
    protein_goal = data.get('protein_goal', details.protein_goal)
    carb_goal = data.get('carb_goal', details.carb_goal)

    if any(value < 0 for value in [age, height, weight, kcal_goal, fat_goal, protein_goal, carb_goal]):
        return jsonify({"error": "Age, height, weight, and goals must be greater than or equal to 0"}), 400

    # Update existing UserDetails
    details.age = age
    details.gender = gender
    details.height = height
    details.weight = weight
    details.kcal_goal = kcal_goal
    details.fat_goal = fat_goal
    details.protein_goal = protein_goal
    details.carb_goal = carb_goal

    db.session.commit()
    return jsonify({"message": "User details updated successfully"}), 200

def get_user_details(user_id):
    details = UserDetails.query.get(user_id)
    if details:
        return jsonify(details.to_dict())
    else:
        return jsonify({"message": "User details not specified"}), 404