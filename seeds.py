from models import db, User, UserDetails, Links, LinkTypes, Diet, UserDiets, Meal, MealCategory, MealIngredients, Ingredients, FoodLog, LocalMeals, FoodSchedule

def seed_database():
    # Dodanie przykładowych użytkowników
    if not User.query.first():
        user1 = User(email="user1@example.com", password="password1", created_at="2024-01-01 12:00:00", email_confirmed=True, active=True)
        user2 = User(email="user2@example.com", password="password2", created_at="2024-01-02 12:00:00", email_confirmed=False, active=True)
        db.session.add_all([user1, user2])
        db.session.commit()

    # Dodanie szczegółów użytkowników
    if not UserDetails.query.first():
        details1 = UserDetails(user_id=1, age=30, gender="M", height=180.0, weight=75.0, kcal_goal=2500, fat_goal=70, protein_goal=150, carb_goal=300)
        details2 = UserDetails(user_id=2, age=25, gender="F", height=165.0, weight=60.0, kcal_goal=2000, fat_goal=60, protein_goal=100, carb_goal=250)
        db.session.add_all([details1, details2])
        db.session.commit()

    # Dodanie typów linków
    if not LinkTypes.query.first():
        link_type1 = LinkTypes(type="activation")
        link_type2 = LinkTypes(type="reset")
        db.session.add_all([link_type1, link_type2])
        db.session.commit()

    # Dodanie linków
    if not Links.query.first():
        link1 = Links(user_id=1, code="abc123", type_id=1, used=False, expire_at="2024-01-10 12:00:00")
        link2 = Links(user_id=2, code="def456", type_id=2, used=True, expire_at="2024-01-11 12:00:00")
        db.session.add_all([link1, link2])
        db.session.commit()

    # Dodanie diet
    if not Diet.query.first():
        diet1 = Diet(name="Keto", description="Low carb, high fat diet")
        diet2 = Diet(name="Vegan", description="Plant-based diet")
        db.session.add_all([diet1, diet2])
        db.session.commit()

    # Dodanie diet użytkowników
    if not UserDiets.query.first():
        user_diet1 = UserDiets(user_id=1, diet_id=1, allowed=True)
        user_diet2 = UserDiets(user_id=2, diet_id=2, allowed=True)
        db.session.add_all([user_diet1, user_diet2])
        db.session.commit()

    # Dodanie kategorii posiłków
    if not MealCategory.query.first():
        category1 = MealCategory(category="Breakfast", description="Morning meal")
        category2 = MealCategory(category="Dinner", description="Evening meal")
        db.session.add_all([category1, category2])
        db.session.commit()

    # Dodanie posiłków
    if not Meal.query.first():
        meal1 = Meal(name="Omelette", description="Egg omelette", creator_id=1, diet_id=1, category_id=1, version=1, last_update="2024-01-01 12:00:00")
        meal2 = Meal(name="Salad", description="Mixed salad", creator_id=2, diet_id=2, category_id=2, version=1, last_update="2024-01-02 12:00:00")
        db.session.add_all([meal1, meal2])
        db.session.commit()

    # Dodanie składników posiłków
    if not MealIngredients.query.first():
        ingredient1 = MealIngredients(meal_id=1, ingredient_id=1, unit="grams", quantity=100.0)
        ingredient2 = MealIngredients(meal_id=2, ingredient_id=2, unit="grams", quantity=200.0)
        db.session.add_all([ingredient1, ingredient2])
        db.session.commit()

    # Dodanie składników
    if not Ingredients.query.first():
        ingredient1 = Ingredients(description="Egg", kcal=155, protein=13, carbs=1, fat=11, brand="BrandA", barcode="123456789")
        ingredient2 = Ingredients(description="Lettuce", kcal=15, protein=1, carbs=2, fat=0, brand="BrandB", barcode="987654321")
        db.session.add_all([ingredient1, ingredient2])
        db.session.commit()

    # Dodanie przykładowych LocalMeals
    if not LocalMeals.query.first():
        meal1 = LocalMeals(composition=1, meal_id=1, meal_version=1)
        meal2 = LocalMeals(composition=2, meal_id=2, meal_version=1)
        meal3 = LocalMeals(composition=3, meal_id=1, meal_version=2)  # Third meal example
        db.session.add_all([meal1, meal2, meal3])
        db.session.commit()

    # Dodanie przykładowych FoodLogs
    if not FoodLog.query.first():
        log1 = FoodLog(local_meal_id=1, portion=1.0, at="2024-12-15 12:00:00")
        log2 = FoodLog(local_meal_id=2, portion=0.5, at="2024-12-15 18:00:00")
        db.session.add_all([log1, log2])
        db.session.commit()

    # Dodanie przykładowych FoodSchedules
    if not FoodSchedule.query.first():
        schedule1 = FoodSchedule(local_meal_id=1, at="2024-12-16 08:00:00")
        schedule2 = FoodSchedule(local_meal_id=2, at="2024-12-16 14:00:00")
        db.session.add_all([schedule1, schedule2])
        db.session.commit()

    print("Database seeded successfully!")
