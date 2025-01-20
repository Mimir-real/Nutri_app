from flask import Flask, jsonify
from config import Config
from models import db
from seeds import seed_database
from flask_migrate import Migrate
from dotenv import load_dotenv
from db_import import import_database
import os
import sys
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate

load_dotenv()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Load from environment variable
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)  # Dodaj tę linię, aby włączyć CORS dla całej aplikacji

def seed_base_database():
    with app.app_context():
        seed_database()
        pass

def seed_data():
    with app.app_context():
        # Call your seed_database function or add your seeding logic here
        # seed_database()
        print("Database seeded successfully.")

@app.cli.command('seed')
def seed():
    seed_data()

# Funkcja do inicjalizacji bazy danych
def setup_database():
    with app.app_context():
        db.create_all()
        if 'dbimport' in sys.argv or 'importdb' in sys.argv:
            print('Importing database, this may take a while')
            import_database()
            print('Importing completed')
        if 'seed' in sys.argv:
            print('Seeding database with base data')
            seed_base_database()
            print('Seeding completed')
        if 'seed' in sys.argv or 'dbimport' in sys.argv or 'importdb' in sys.argv:
            exit()

# Registration Form
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Length(max=128)])
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
#     confirm_password = PasswordField(
#         'Confirm Password', validators=[DataRequired(), EqualTo('password')],
#     )
#     submit = SubmitField('Register')

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user:
#             raise ValidationError('User with that email already exists.')


# User Endpoints
from endpoints.users import create_user, get_users, get_user, activate_user, deactivate_user
app.add_url_rule('/users', view_func=create_user, methods=['POST'])
app.add_url_rule('/users', view_func=get_users, methods=['GET'])
app.add_url_rule('/users/<int:user_id>', view_func=get_user, methods=['GET'])
app.add_url_rule('/users/<int:user_id>/activate', view_func=activate_user, methods=['GET'])
app.add_url_rule('/users/<int:user_id>', view_func=deactivate_user, methods=['DELETE'])

# User Details Endpoints
from endpoints.user_details import create_user_details, update_user_details, get_user_details
app.add_url_rule('/users/<int:user_id>/details', view_func=create_user_details, methods=['POST'])
app.add_url_rule('/users/<int:user_id>/details', view_func=update_user_details, methods=['PUT', 'PATCH'])
app.add_url_rule('/users/<int:user_id>/details', view_func=get_user_details, methods=['GET'])

# Diets Endpoints
from endpoints.diets import create_diet, get_diets, get_diet
app.add_url_rule('/diets', view_func=create_diet, methods=['POST'])
app.add_url_rule('/diets', view_func=get_diets, methods=['GET'])
app.add_url_rule('/diets/<int:diet_id>', view_func=get_diet, methods=['GET'])

# User Diets Endpoints
from endpoints.user_diets import assign_diet_to_user, remove_diet_from_user, get_user_diets
app.add_url_rule('/users/<int:user_id>/diets', view_func=assign_diet_to_user, methods=['POST'])
app.add_url_rule('/users/<int:user_id>/diets/<int:diet_id>', view_func=remove_diet_from_user, methods=['DELETE'])
app.add_url_rule('/users/<int:user_id>/diets', view_func=get_user_diets, methods=['GET'])

# Meals Endpoints
from endpoints.meals import get_meals, get_meal, create_meal, update_meal, delete_meal, search_meals
app.add_url_rule('/meals', view_func=get_meals, methods=['GET'])
app.add_url_rule('/meals/<int:meal_id>', view_func=get_meal, methods=['GET'])
app.add_url_rule('/meals/search', view_func=search_meals, methods=['GET'])
app.add_url_rule('/meals', view_func=create_meal, methods=['POST'])
app.add_url_rule('/meals/<int:meal_id>', view_func=update_meal, methods=['PUT', 'PATCH'])
app.add_url_rule('/meals/<int:meal_id>', view_func=delete_meal, methods=['DELETE'])

# Meal Categories Endpoints
from endpoints.meal_category import assign_category_to_meal, remove_category_from_meal, update_category_of_meal
app.add_url_rule('/meals/<int:meal_id>/category', view_func=assign_category_to_meal, methods=['POST'])
app.add_url_rule('/meals/<int:meal_id>/category', view_func=remove_category_from_meal, methods=['DELETE'])
app.add_url_rule('/meals/<int:meal_id>/category', view_func=update_category_of_meal, methods=['PUT'])

# Meal Diet Endpoints
from endpoints.meal_diet import assign_diet_to_meal, remove_diet_from_meal, update_diet_of_meal
app.add_url_rule('/meals/<int:meal_id>/diet', view_func=assign_diet_to_meal, methods=['POST'])
app.add_url_rule('/meals/<int:meal_id>/diet', view_func=remove_diet_from_meal, methods=['DELETE'])
app.add_url_rule('/meals/<int:meal_id>/diet', view_func=update_diet_of_meal, methods=['PUT'])


# Meal Ingredients Endpoints
from endpoints.meal_ingredients import get_meal_ingredients, replace_meal_ingredients, add_meal_ingredient, remove_meal_ingredient
app.add_url_rule('/meals/<int:meal_id>/ingredients', view_func=get_meal_ingredients, methods=['GET'])
app.add_url_rule('/meals/<int:meal_id>/ingredients', view_func=replace_meal_ingredients, methods=['PUT'])
app.add_url_rule('/meals/<int:meal_id>/ingredients', view_func=add_meal_ingredient, methods=['POST'])
app.add_url_rule('/meals/<int:meal_id>/ingredients/<int:ingredient_id>', view_func=remove_meal_ingredient, methods=['DELETE'])


# Ingredients Endpoints

# Brak POST dla składników - Składniki będą dodawane z formularza dodawania/aktualizacji posiłku
# Składniki wybrane w posiłku będą importowane do bazy danych z zewnętrznej bazy OpenFoodFacts

from endpoints.ingredients import get_ingredients, get_ingredient_by_id, search_ingredients
app.add_url_rule('/ingredients', view_func=get_ingredients, methods=['GET'])
app.add_url_rule('/ingredients/<int:ing_id>', view_func=get_ingredient_by_id, methods=['GET'])
app.add_url_rule('/ingredients/search/<query>', view_func=search_ingredients, methods=['GET'])

# Food schedule Endpoints

from endpoints.food_schedule import get_food_schedules, get_food_schedule, create_food_schedule, delete_food_schedule
app.add_url_rule('/food/schedules', view_func=get_food_schedules, methods=['GET'])
app.add_url_rule('/food/schedules', view_func=create_food_schedule, methods=['POST'])
app.add_url_rule('/food/schedules/<int:schedule_id>', view_func=get_food_schedule, methods=['GET'])
app.add_url_rule('/food/schedules/<int:schedule_id>', view_func=delete_food_schedule, methods=['DELETE'])

from endpoints.shopping_list import generate_shopping_list
app.add_url_rule('/users/<int:user_id>/shopping_list', view_func=generate_shopping_list, methods=['GET'])

# Login & Register Endpoints

from endpoints.auth import login, register

app.add_url_rule('/login', view_func=login, methods=['POST'])
# app.add_url_rule('/register', view_func=register, methods=['POST'])

# Przykład zabezpieczonego endpointu
# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#     return jsonify({"message": f"Hello, {user.email}!"}), 200

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
