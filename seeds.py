from datetime import datetime
from models import db, User, UserDetails, LinkTypes, Links, Diet, UserDiets, Meal, MealCategory, MealIngredients, Ingredients, LocalMeals, FoodLog, FoodSchedule

def seed_database():
    # Tworzenie przykładowych użytkowników
    user1 = User(email="user1@example.com", password="password1", email_confirmed=True, active=True, created_at=datetime.utcnow())
    user2 = User(email="user2@example.com", password="password2", email_confirmed=False, active=True, created_at=datetime.utcnow())
    
    db.session.add_all([user1, user2])
    db.session.commit()

    # Tworzenie przykładowych detali użytkowników
    user_details1 = UserDetails(user_id=user1.id, age=25, gender="M", height=175.5, weight=70, kcal_goal=2500, fat_goal=70, protein_goal=150, carb_goal=300)
    user_details2 = UserDetails(user_id=user2.id, age=30, gender="F", height=160.0, weight=55, kcal_goal=2000, fat_goal=60, protein_goal=100, carb_goal=250)
    
    db.session.add_all([user_details1, user_details2])
    db.session.commit()

    # Tworzenie typów linków
    link_type1 = LinkTypes(type="Invite")
    link_type2 = LinkTypes(type="Password Reset")
    
    db.session.add_all([link_type1, link_type2])
    db.session.commit()

    # Tworzenie linków dla użytkowników
    link1 = Links(user_id=user1.id, code="invite123", type_id=link_type1.id, used=False, expire_at=datetime.utcnow())
    link2 = Links(user_id=user2.id, code="reset123", type_id=link_type2.id, used=False, expire_at=datetime.utcnow())
    
    db.session.add_all([link1, link2])
    db.session.commit()

    # Tworzenie diet
    diet1 = Diet(name="Keto", description="Low-carb, high-fat diet.")
    diet2 = Diet(name="Vegan", description="Plant-based diet without animal products.")
    
    db.session.add_all([diet1, diet2])
    db.session.commit()

    # Przypisywanie diet do użytkowników
    user_diet1 = UserDiets(user_id=user1.id, diet_id=diet1.id, allowed=True)
    user_diet2 = UserDiets(user_id=user2.id, diet_id=diet2.id, allowed=True)
    
    db.session.add_all([user_diet1, user_diet2])
    db.session.commit()

    # Tworzenie kategorii posiłków
    category1 = MealCategory(category="Breakfast", description="Morning meal")
    category2 = MealCategory(category="Lunch", description="Midday meal")
    
    db.session.add_all([category1, category2])
    db.session.commit()

    # Tworzenie składników
    ingredient1 = Ingredients(description="Chicken breast", kcal=165, protein=31, carbs=0, fat=3, brand="BrandA", barcode="123456")
    ingredient2 = Ingredients(description="Broccoli", kcal=55, protein=4, carbs=11, fat=0, brand="BrandB", barcode="789012")
    
    db.session.add_all([ingredient1, ingredient2])
    db.session.commit()

    # Tworzenie posiłków
    meal1 = Meal(name="Chicken Salad", description="Grilled chicken with mixed greens", creator_id=user1.id, diet_id=diet1.id, category_id=category1.id, version=1, last_update=datetime.utcnow())
    meal2 = Meal(name="Vegan Buddha Bowl", description="A variety of vegetables with quinoa", creator_id=user2.id, diet_id=diet2.id, category_id=category2.id, version=1, last_update=datetime.utcnow())
    
    db.session.add_all([meal1, meal2])
    db.session.commit()

    # Przypisywanie składników do posiłków
    meal_ingredient1 = MealIngredients(meal_id=meal1.id, ingredient_id=ingredient1.id, unit="g", quantity=200)
    meal_ingredient2 = MealIngredients(meal_id=meal2.id, ingredient_id=ingredient2.id, unit="g", quantity=150)
    
    db.session.add_all([meal_ingredient1, meal_ingredient2])
    db.session.commit()

    # Tworzenie lokalnych posiłków
    local_meal1 = LocalMeals(composition=1, meal_id=meal1.id, meal_version=1)
    local_meal2 = LocalMeals(composition=2, meal_id=meal2.id, meal_version=1)
    
    db.session.add_all([local_meal1, local_meal2])
    db.session.commit()

    # Tworzenie harmonogramów posiłków
    food_schedule1 = FoodSchedule(local_meal_id=local_meal1.id, at=datetime(2024, 12, 28, 8, 30))
    food_schedule2 = FoodSchedule(local_meal_id=local_meal2.id, at=datetime(2024, 12, 28, 12, 30))
    
    db.session.add_all([food_schedule1, food_schedule2])
    db.session.commit()

    # Tworzenie logów żywnościowych
    food_log1 = FoodLog(local_meal_id=local_meal1.id, portion=1, at=datetime.utcnow())
    food_log2 = FoodLog(local_meal_id=local_meal2.id, portion=1.5, at=datetime.utcnow())
    
    db.session.add_all([food_log1, food_log2])
    db.session.commit()
