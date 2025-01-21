from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, event, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()

# Model do OpenFoodFacts

class Ingredients(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    product_name = db.Column(db.String)
    generic_name = db.Column(db.String)
    kcal_100g = db.Column(db.Float)
    protein_100g = db.Column(db.Float)
    carbs_100g = db.Column(db.Float)
    fat_100g = db.Column(db.Float)
    brand = db.Column(db.String)
    barcode = db.Column(db.String)
    image_url = db.Column(db.String)
    labels_tags = db.Column(db.String)
    product_quantity = db.Column(db.Float)
    allergens = db.Column(db.String)
    tsv = db.Column(TSVECTOR)

    __table_args__ = (
        Index('tsv_idx', 'tsv', postgresql_using='gin'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'generic_name': self.generic_name,
            'kcal_100g': self.kcal_100g,
            'protein_100g': self.protein_100g,
            'carbs_100g': self.carbs_100g,
            'fat_100g': self.fat_100g,
            'brand': self.brand,
            'barcode': self.barcode,
            'image_url': self.image_url,
            'labels_tags': self.labels_tags,
            'product_quantity': self.product_quantity,
            'allergens': self.allergens,
        }

def update_tsvector(mapper, connection, target):
    connection.execute(
        Ingredients.__table__.update().
        where(Ingredients.id == target.id).
        values(
            tsv=func.to_tsvector('english', target.product_name + ' ' + target.generic_name)
        )
    )

# Wyzwalacz do aktualizacji kolumn tsv przy każdej zmianie danych
event.listen(Ingredients, 'after_insert', update_tsvector)
event.listen(Ingredients, 'after_update', update_tsvector)

# Modele ogólne
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    email_confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    # Password nie powinien być zwracany w API
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'email_confirmed': self.email_confirmed,
            'active': self.active
        }


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

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'kcal_goal': self.kcal_goal,
            'fat_goal': self.fat_goal,
            'protein_goal': self.protein_goal,
            'carb_goal': self.carb_goal
        }

class Links(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(128))
    type_id = db.Column(db.Integer, db.ForeignKey('link_types.id'))
    used = db.Column(db.Boolean, default=False)
    expire_at = db.Column(db.DateTime)

    # Code jest jak token, więc nie powinien być zwracany w API
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type_id': self.type_id,
            'used': self.used,
            'expire_at': self.expire_at
        }

class LinkTypes(db.Model):
    __tablename__ = 'link_types'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type
        }

# MODELE DIET I POSIŁKÓW
class Diet(db.Model):
    __tablename__ = 'diet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class UserDiets(db.Model):
    __tablename__ = 'user_diets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diet_id = db.Column(db.Integer, db.ForeignKey('diet.id'), nullable=False)
    allowed = db.Column(db.Boolean, default=True)

    __table_args__ = (UniqueConstraint('user_id', 'diet_id', name='_user_diet_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'diet_id': self.diet_id,
            'allowed': self.allowed
        }

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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'diet_id': self.diet_id,
            'category_id': self.category_id,
            'version': self.version,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else None
        }

    def save_meal_version(self):
        # Check if the version already exists in MealHistory
        existing_version = MealHistory.query.filter_by(meal_id=self.id, meal_version=self.version).first()
        if existing_version:
            return  # Version already exists, do not save again

        # Get meal ingredients
        meal_ingredients = MealIngredients.query.filter_by(meal_id=self.id).all()
        ingredients = [ingredient.to_dict() for ingredient in meal_ingredients]

        meal_history = MealHistory(
            composition={
                'meal': self.to_dict(),
                'ingredients': ingredients
            },
            meal_id=self.id,
            meal_version=self.version
        )
        db.session.add(meal_history)
        db.session.commit()
    
    def calculate_nutrients(self):
        meal_ingredients = MealIngredients.query.filter_by(meal_id=self.id).all()
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for ingredient in meal_ingredients:
            ingredient_details = Ingredients.query.get(ingredient.ingredient_id)
            if ingredient_details:
                if ingredient_details.kcal_100g:
                    total_calories += (ingredient.quantity * ingredient_details.kcal_100g) / 100
                if ingredient_details.protein_100g:
                    total_protein += (ingredient.quantity * ingredient_details.protein_100g) / 100
                if ingredient_details.carbs_100g:
                    total_carbs += (ingredient.quantity * ingredient_details.carbs_100g) / 100
                if ingredient_details.fat_100g:
                    total_fat += (ingredient.quantity * ingredient_details.fat_100g) / 100
        return {
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        }
    
    def calculate_total_weight(self):
        meal_ingredients = MealIngredients.query.filter_by(meal_id=self.id).all()
        total_weight = sum(ingredient.quantity for ingredient in meal_ingredients)
        return total_weight
        
class MealCategory(db.Model):
    __tablename__ = 'meal_category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'description': self.description
        }

class MealIngredients(db.Model):
    __tablename__ = 'meal_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
    unit = db.Column(db.String(255))
    quantity = db.Column(db.Float)

    __table_args__ = (UniqueConstraint('meal_id', 'ingredient_id', name='_meal_ingredient_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'meal_id': self.meal_id,
            'ingredient_id': self.ingredient_id,
            'unit': self.unit,
            'quantity': self.quantity
        }

# Zmiana LocalMeals -> MealHistory
class MealHistory(db.Model):
    __tablename__ = 'meal_history'
    id = db.Column(db.Integer, primary_key=True)
    composition = db.Column(db.JSON)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id')) # Odnosi się do ID Posiłku
    meal_version = db.Column(db.Integer) # Odnosi się do wersji Posiłku

    def to_dict(self):
        return {
            'id': self.id,
            'composition': self.composition,
            'meal_id': self.meal_id,
            'meal_version': self.meal_version
        }

    def calculate_nutrients(self):
        ingredients = self.composition.get('ingredients', [])
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for ingredient in ingredients:
            ingredient_details = Ingredients.query.get(ingredient['ingredient_id'])
            if ingredient_details:
                if ingredient_details.kcal_100g:
                    total_calories += (ingredient['quantity'] * ingredient_details.kcal_100g) / 100
                if ingredient_details.protein_100g:
                    total_protein += (ingredient['quantity'] * ingredient_details.protein_100g) / 100
                if ingredient_details.carbs_100g:
                    total_carbs += (ingredient['quantity'] * ingredient_details.carbs_100g) / 100
                if ingredient_details.fat_100g:
                    total_fat += (ingredient['quantity'] * ingredient_details.fat_100g) / 100
        return {
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        }

    def calculate_total_weight(self):
        ingredients = self.composition.get('ingredients', [])
        total_weight = sum(ingredient['quantity'] for ingredient in ingredients)
        return total_weight

class FoodSchedule(db.Model):
    __tablename__ = 'food_schedule'
    id = db.Column(db.Integer, primary_key=True)
    meal_history_id = db.Column(db.Integer, db.ForeignKey('meal_history.id'))
    at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Odnosi się do ID użytkownika

    def to_dict(self):
        return {
            'id': self.id,
            'meal_history_id': self.meal_history_id,
            'at': self.at,
            'user_id': self.user_id
        }

class FoodLog(db.Model):
    __tablename__ = 'food_log'
    id = db.Column(db.Integer, primary_key=True)
    meal_history_id = db.Column(db.Integer, db.ForeignKey('meal_history.id'))
    portion = db.Column(db.Float)
    at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Odnosi się do ID użytkownika

    def to_dict(self):
        return {
            'id': self.id,
            'meal_history_id': self.meal_history_id,
            'portion': self.portion,
            'at': self.at,
            'user_id': self.user_id
        }