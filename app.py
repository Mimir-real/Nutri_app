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
import os

load_dotenv()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# Funkcja do inicjalizacji bazy danych
def setup_database():
    with app.app_context():
        db.create_all()
        seed_database()

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

        # Tworzymy nowego uzytkownika
        new_user = User(
            email=data['email'], 
            password=data['password'], 
            email_confirmed=data.get('email_confirmed', False), 
            active=data.get('active', True)
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created", "user_id": new_user.id}), 201

    except ValueError as e:
        # W przypadku, gdy 'email' lub 'password' są puste, zwroc blad 400 (Bad Request)
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        # W przypadku innych bledow, zwroc blad 500 (Internal Server Error)
        return jsonify({"error": "An error occurred while creating the user", "message": str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{ "id": user.id, "email": user.email, "active": user.active } for user in users])

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.email = data.get('email', user.email)
    user.active = data.get('active', user.active)
    db.session.commit()
    return jsonify({"message": "User updated"})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

# ==================== USER DETAILS CRUD ====================
@app.route('/user_details', methods=['POST'])
def create_user_details():
    data = request.get_json()
    new_details = UserDetails(user_id=data['user_id'], age=data['age'], gender=data['gender'], height=data['height'], weight=data['weight'])
    db.session.add(new_details)
    db.session.commit()
    return jsonify({"message": "User details created"}), 201

@app.route('/user_details/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    details = UserDetails.query.get_or_404(user_id)
    return jsonify({"user_id": details.user_id, "age": details.age, "gender": details.gender})

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
    return jsonify([{ "id": diet.id, "name": diet.name, "description": diet.description } for diet in diets])

# ==================== MEAL CRUD ====================
@app.route('/meals', methods=['POST'])
def create_meal():
    data = request.get_json()
    new_meal = Meal(name=data['name'], description=data.get('description'), creator_id=data['creator_id'], version=data.get('version', 1))
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({"message": "Meal created", "meal_id": new_meal.id}), 201

@app.route('/meals', methods=['GET'])
def get_meals():
    meals = Meal.query.all()
    return jsonify([{ "id": meal.id, "name": meal.name, "description": meal.description } for meal in meals])

@app.route('/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Meal deleted"})

# ==================== INGREDIENT CRUD ====================
@app.route('/ingredients', methods=['POST'])
def create_ingredient():
    data = request.get_json()
    new_ingredient = Ingredients(description=data['description'], kcal=data['kcal'], protein=data['protein'], carbs=data['carbs'], fat=data['fat'])
    db.session.add(new_ingredient)
    db.session.commit()
    return jsonify({"message": "Ingredient created", "ingredient_id": new_ingredient.id}), 201

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = Ingredients.query.all()
    return jsonify([{ "id": ing.id, "description": ing.description, "kcal": ing.kcal } for ing in ingredients])

# ==================== FOOD LOG CRUD ====================
@app.route('/food_logs', methods=['POST'])
def create_food_log():
    data = request.get_json()
    new_log = FoodLog(local_meal_id=data['local_meal_id'], portion=data['portion'], at=data['at'])
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"message": "Food log created", "food_log_id": new_log.id}), 201

@app.route('/food_logs', methods=['GET'])
def get_food_logs():
    logs = FoodLog.query.all()
    return jsonify([{ "id": log.id, "portion": log.portion, "at": log.at } for log in logs])

# ==================== FOOD SCHEDULE CRUD ====================
@app.route('/food_schedules', methods=['POST'])
def create_food_schedule():
    data = request.get_json()
    new_schedule = FoodSchedule(local_meal_id=data['local_meal_id'], at=data['at'])
    db.session.add(new_schedule)
    db.session.commit()
    return jsonify({"message": "Food schedule created", "schedule_id": new_schedule.id}), 201

@app.route('/food_schedules', methods=['GET'])
def get_food_schedules():
    schedules = FoodSchedule.query.all()
    return jsonify([{ "id": s.id, "local_meal_id": s.local_meal_id, "at": s.at } for s in schedules])

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

