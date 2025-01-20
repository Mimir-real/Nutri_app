from flask import request, jsonify
from models import db, User, Links
import uuid
from sqlalchemy.exc import IntegrityError

def create_user():
    try:
        data = request.get_json()

        # Sprawdzamy, czy pola 'email' i 'password' są puste
        if not data.get('email') or not data.get('password'):
            raise ValueError("Email and password are required")

        # Tworzymy nowego użytkownika
        new_user = User(
            email=data['email'], 
            password=data['password'], 
            email_confirmed=False,
            active=False,
            created_at=db.func.now()
        )

        db.session.add(new_user)
        db.session.commit()

        # Generate a unique activation code
        activation_code = str(uuid.uuid4())

        # Save the activation code in the Links table
        activation_link = Links(
            user_id=new_user.id,
            code=activation_code,
            type_id=1,  # 1 = activation link (in the LinkTypes table, type = "Invite")
            used=False
        )

        db.session.add(activation_link)
        db.session.commit()

        return jsonify({"message": "User created", "user_id": new_user.id, "activation_code (wyświetlane dla celów prezentacyjnych)": activation_code}), 201

    except ValueError as e:
        # W przypadku, gdy 'email' lub 'password' są puste, zwróć błąd 400 (Bad Request)
        print('POST /users - ValueError:', e)
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError as e:
        # W przypadku naruszenia unikalności, zwróć błąd 400 (Bad Request)
        print('POST /users - IntegrityError:', e)
        db.session.rollback()
        return jsonify({"error": "User with this email already exists"}), 400
    
    except Exception as e:
        # W przypadku innych błędów, zwróć błąd 500 (Internal Server Error)
        print('POST /users - Exception:', e)
        return jsonify({"error": "An error occurred while creating the user", "message": str(e)}), 500

def get_users():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)

    if limit < 1 or page < 1:
        return jsonify({"error": "Limit and page must be positive integers"}), 400

    users_pagination = User.query.paginate(page=page, per_page=limit, max_per_page=100, error_out=False)
    users = users_pagination.items
    return jsonify({
        "users": [user.to_dict() for user in users],
        "total": users_pagination.total,
        "pages": users_pagination.pages,
        "current_page": users_pagination.page,
        "page_size": users_pagination.per_page
    })

def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

def activate_user(user_id):
    code = request.args.get('code')
    email = request.args.get('email')

    if not code or not email:
        return jsonify({"error": "Code and email are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email != email:
        return jsonify({"error": "Email does not match"}), 400

    link = Links.query.filter_by(user_id=user_id, code=code).first()
    if not link:
        return jsonify({"error": "Invalid code"}), 400

    user.active = True
    user.email_confirmed = True
    db.session.delete(link)
    db.session.commit()

    return jsonify({"message": "User activated successfully"}), 200

def deactivate_user(user_id):
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password is required"}), 400

    user = User.query.get_or_404(user_id)

    if user.password != password:
        return jsonify({"error": "Incorrect password"}), 401

    user.active = False
    db.session.commit()
    return jsonify({"message": "User deactivated"})