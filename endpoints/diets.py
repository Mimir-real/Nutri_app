from flask import request, jsonify
from models import db, Diet

def create_diet():
    data = request.get_json()
    new_diet = Diet(name=data['name'], description=data.get('description'))
    db.session.add(new_diet)
    db.session.commit()
    return jsonify({"message": "Diet created", "diet_id": new_diet.id}), 201

def get_diets():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    diets_pagination = Diet.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    diets = diets_pagination.items
    return jsonify({
        "diets": [diet.to_dict() for diet in diets],
        "total": diets_pagination.total,
        "pages": diets_pagination.pages,
        "current_page": diets_pagination.page,
        "page_size": diets_pagination.per_page
    })

def get_diet(diet_id):
    diet = Diet.query.get_or_404(diet_id)
    return jsonify(diet.to_dict())