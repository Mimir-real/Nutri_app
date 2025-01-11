from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from config import Config
from models import db, User, UserDetails, Links, LinkTypes, Diet, UserDiets, Meal, MealCategory, MealIngredients, Ingredients, FoodLog, LocalMeals, FoodSchedule
from seeds import seed_database
from flask_migrate import Migrate
from dotenv import load_dotenv
from db_import import import_database
import os
import sys
import uuid
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

load_dotenv()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

def seed_base_database():
    with app.app_context():
        seed_database()

# Funkcja do inicjalizacji bazy danych
def setup_database():
    with app.app_context():
        db.create_all()
        if 'dbimport' in sys.argv or 'importdb' in sys.argv:
            print('Importing database, this may take a while')
            import_database()
            print('Importing completed')
            seed_database()
            exit()

# Registration Form
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')],
    )
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('User with that email already exists.')

# ==================== USER CRUD ====================
@app.route('/users', methods=['POST'])
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
            active=False
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
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError as e:
        # W przypadku naruszenia unikalności, zwróć błąd 400 (Bad Request)
        db.session.rollback()
        return jsonify({"error": "User with this email already exists"}), 400
    
    except Exception as e:
        # W przypadku innych błędów, zwróć błąd 500 (Internal Server Error)
        return jsonify({"error": "An error occurred while creating the user", "message": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@app.route('/users/<int:user_id>/activate', methods=['GET'])
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

@app.route('/users/<int:user_id>', methods=['DELETE'])
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

# ==================== USER DETAILS CRUD ====================

@app.route('/user_details/<int:user_id>', methods=['POST'])
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

@app.route('/user_details/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user_details(user_id):
    data = request.get_json()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    details = UserDetails.query.get_or_404(user_id)

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

@app.route('/user_details/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    details = UserDetails.query.get_or_404(user_id)
    return jsonify(details.to_dict())

# ==================== DIET CRUD ====================
@app.route('/diets', methods=['POST'])
def create_diet():
    data = request.get_json()
    new_diet = Diet(name=data['name'], description=data.get('description'))
    db.session.add(new_diet)
    db.session.commit()
    return jsonify({"message": "Diet created", "diet_id": new_diet.id}), 201

@app.route('/diets', methods=['GET'])
def get_diets():
    diets = Diet.query.all()
    return jsonify([diet.to_dict() for diet in diets])

@app.route('/diets/<int:diet_id>', methods=['GET'])
def get_diet(diet_id):
    diet = Diet.query.get_or_404(diet_id)
    return jsonify(diet.to_dict())


# ==================== USER & DIETS ====================

@app.route('/users/<int:user_id>/diets', methods=['POST'])
def assign_diet_to_user(user_id):
    data = request.get_json()
    if not user_id or not data.get('diet_id'):
        return jsonify({"error": "diet_id is required"}), 400

    user = User.query.get_or_404(user_id)
    diet = Diet.query.get_or_404(data['diet_id'])

    allowed = data.get('allowed', True)  # Default to True if 'allowed' is not provided

    user_diet = UserDiets(user_id=user_id, diet_id=data['diet_id'], allowed=allowed)
    db.session.add(user_diet)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This user already has this diet assigned"}), 400

    return jsonify({"message": "Diet assigned to user"}), 201

@app.route('/users/<int:user_id>/diets/<int:diet_id>', methods=['DELETE'])
def remove_diet_from_user(user_id, diet_id):
    user_diet = UserDiets.query.filter_by(user_id=user_id, diet_id=diet_id).first()
    if not user_diet:
        return jsonify({"error": "User diet not found"}), 404

    db.session.delete(user_diet)
    db.session.commit()
    return jsonify({"message": "Diet removed from user"})

@app.route('/users/<int:user_id>/diets', methods=['GET'])
def get_user_diets(user_id):
    user_diets = UserDiets.query.filter_by(user_id=user_id).all()
    return jsonify([ud.to_dict() for ud in user_diets])

# ==================== MEAL CRUD ====================

@app.route('/meals', methods=['POST'])
def create_meal():
    data = request.get_json()

    # Validate required fields
    if not data.get('name') or not data.get('creator_id'):
        return jsonify({"error": "Name and creator_id are required"}), 400
    
    # Zakładamy że w sesji jest zapisane user_id (creator_id)
    # My bierzemy je z body dla celów prezentacyjnych
    creator_id = data.get('creator_id')

    # Create new meal
    new_meal = Meal(
        name=data.get('name'),
        description=data.get('description', ""),
        creator_id=creator_id,
        diet_id=data.get('diet_id'),
        category_id=data.get('category_id'),
        version=1,
        last_update=datetime.utcnow()
    )
    db.session.add(new_meal)
    db.session.commit()


    ingredients = data.get('ingredients', [])
    
    for ingredient in ingredients:
        meal_ingredient = MealIngredients(
            meal_id=new_meal.id,
            ingredient_id=ingredient['ingredient_id'],
            unit=ingredient['unit'],
            quantity=ingredient['quantity']
        )
        db.session.add(meal_ingredient)

    db.session.commit()
    return jsonify({"message": "Meal created", "meal_id": new_meal.id}), 201

@app.route('/meals/<int:meal_id>', methods=['PUT', 'PATCH'])
def update_meal(meal_id):
    data = request.get_json()

    # Fetch the meal to be updated
    meal = Meal.query.get_or_404(meal_id)

    # Update meal details
    meal.name = data.get('name', meal.name)
    meal.description = data.get('description', meal.description)
    meal.diet_id = data.get('diet_id', meal.diet_id)
    meal.category_id = data.get('category_id', meal.category_id)
    meal.version += 1
    meal.last_update = datetime.utcnow()

    db.session.commit()

    # TODO: Do odkomentowania i implementacji po dodaniu integracji z OpenFoodFacts
    # # Update ingredients if provided
    # if 'ingredients' in data:
    #     # Remove existing ingredients
    #     MealIngredients.query.filter_by(meal_id=meal.id).delete()
    #     # Add new ingredients
    #     for ingredient in data['ingredients']:
    #         meal_ingredient = MealIngredients(
    #             meal_id=meal.id,
    #             ingredient_id=ingredient['ingredient_id'],
    #             unit=ingredient['unit'],
    #             quantity=ingredient['quantity']
    #         )
    #         db.session.add(meal_ingredient)

    db.session.commit()
    return jsonify({"message": "Meal updated", "meal_id": meal.id}), 200

@app.route('/meals', methods=['GET'])
def get_meals():
    meals = Meal.query.all()
    return jsonify([meal.to_dict() for meal in meals])

@app.route('/meals/<int:meal_id>', methods=['GET'])
def get_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    return jsonify(meal.to_dict())

@app.route('/meals/<int:meal_id>/ingredients', methods=['GET'])
def get_meal_ingredients(meal_id):
    # Fetch meal ingredients with actual ingredient details
    ingredients = db.session.query(MealIngredients, Ingredients).join(Ingredients, MealIngredients.ingredient_id == Ingredients.id).filter(MealIngredients.meal_id == meal_id).all()

    # Map the results to a list of dictionaries
    result = []
    for meal_ingredient, ingredient in ingredients:
        result.append({
            'id': meal_ingredient.id,
            'meal_id': meal_ingredient.meal_id,
            'ingredient_id': meal_ingredient.ingredient_id,
            'quantity': meal_ingredient.quantity,
            'unit': meal_ingredient.unit,
            'ingredient': ingredient.to_dict()
        })

    return jsonify(result)

@app.route('/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Meal deleted"})

# ==================== INGREDIENT CRUD ====================

# Brak POST dla składników - Składniki będą dodawane z formularza dodawania/aktualizacji posiłku
# Składniki wybrane w posiłku będą importowane do bazy danych z zewnętrznej bazy OpenFoodFacts

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = Ingredients.query.all()
    return jsonify([ing.to_dict() for ing in ingredients])

@app.route('/ingredients/<int:ing_id>', methods=['GET'])
def get_ingredient_by_id(ing_id):
    ingredient = Ingredients.query.get_or_404(ing_id)
    return jsonify(ingredient.to_dict())

@app.route('/ingredients/search/<query>')
def search_ingredients(query):
    top = request.args.get('top', default=10, type=int)
    
    # Use full-text search for better matching
    results = Ingredients.query.filter(
        func.to_tsvector('english', Ingredients.product_name + ' ' + Ingredients.generic_name).match(query)
    ).limit(top).all()
    
    # Return all fields in the row
    return jsonify([{
        column.name: getattr(item, column.name)
        for column in Ingredients.__table__.columns
    } for item in results])

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

# ==================== URUCHOMIENIE APLIKACJI ====================
if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
    
# ==================== ERROR HANDLERY =============================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404
    
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400

