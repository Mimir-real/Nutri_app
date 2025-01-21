from flask import request, jsonify
from models import db, Diet, User, UserDiets
from sqlalchemy.exc import IntegrityError

def assign_diet_to_user(user_id):
    data = request.get_json()
    if not user_id or not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    diet = Diet.query.get(data['diet_id'])
    if not diet:
        return jsonify({"message": "Diet not found"}), 404

    allowed = data.get('allowed', True)  # Default to True if 'allowed' is not provided

    user_diet = UserDiets(user_id=user_id, diet_id=data['diet_id'], allowed=allowed)
    db.session.add(user_diet)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This user already has this diet assigned"}), 400

    return jsonify({"message": "Diet assigned to user"}), 201

def remove_diet_from_user(user_id, diet_id):
    user_diet = UserDiets.query.filter_by(user_id=user_id, diet_id=diet_id).first()
    if not user_diet:
        return jsonify({"error": "User diet not found"}), 404

    db.session.delete(user_diet)
    db.session.commit()
    return jsonify({"message": "Diet removed from user"})

def get_user_diets(user_id):
    user_diets = UserDiets.query.filter_by(user_id=user_id).all()
    return jsonify([ud.to_dict() for ud in user_diets])
