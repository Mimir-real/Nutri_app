from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# MODELE OGÓLNE
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    email_confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    age = db.Column(db.SmallInteger)
    gender = db.Column(db.String(1))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    kcal_goal = db.Column(db.SmallInteger)
    fat_goal = db.Column(db.SmallInteger)
    protein_goal = db.Column(db.SmallInteger)
    carb_goal = db.Column(db.SmallInteger)

class Links(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(128))
    type_id = db.Column(db.Integer, db.ForeignKey('link_types.id'))
    used = db.Column(db.Boolean, default=False)
    expire_at = db.Column(db.DateTime)

class LinkTypes(db.Model):
    __tablename__ = 'link_types'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))

# MODELE DIET I POSIŁKÓW
class Diet(db.Model):
    __tablename__ = 'diet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)

class UserDiets(db.Model):
    __tablename__ = 'user_diets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diet_id = db.Column(db.Integer, db.ForeignKey('diet.id'))
    allowed = db.Column(db.Boolean, default=True)

class Meal(db.Model):
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diet_id = db.Column(db.Integer, db.ForeignKey('diet.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('meal_category.id'))
    version = db.Column(db.Integer)
    last_update = db.Column(db.DateTime)

class MealCategory(db.Model):
    __tablename__ = 'meal_category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))
    description = db.Column(db.String(255))

class MealIngredients(db.Model):
    __tablename__ = 'meal_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
    unit = db.Column(db.String(255))
    quantity = db.Column(db.Float)

class Ingredients(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    kcal = db.Column(db.SmallInteger)
    protein = db.Column(db.SmallInteger)
    carbs = db.Column(db.SmallInteger)
    fat = db.Column(db.SmallInteger)
    brand = db.Column(db.String(255))
    barcode = db.Column(db.String(255))

# MODELE LOKALNE
class FoodLog(db.Model):
    __tablename__ = 'food_log'
    id = db.Column(db.Integer, primary_key=True)
    local_meal_id = db.Column(db.Integer, db.ForeignKey('local_meals.id'))
    portion = db.Column(db.Float)
    at = db.Column(db.DateTime)

class LocalMeals(db.Model):
    __tablename__ = 'local_meals'
    id = db.Column(db.Integer, primary_key=True)
    composition = db.Column(db.Integer)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    meal_version = db.Column(db.Integer)

class FoodSchedule(db.Model):
    __tablename__ = 'food_schedule'
    id = db.Column(db.Integer, primary_key=True)
    local_meal_id = db.Column(db.Integer, db.ForeignKey('local_meals.id'))
    at = db.Column(db.DateTime)