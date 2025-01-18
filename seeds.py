from datetime import datetime
from models import db, User, UserDetails, Diet, UserDiets, MealCategory, Meal

def seed_database():
    # Check if users already exist
    user1 = User.query.filter_by(email="user1@example.com").first()
    user2 = User.query.filter_by(email="user2@example.com").first()

    if not user1:
        user1 = User(email="user1@example.com", password="password1", created_at=datetime.utcnow(), email_confirmed=True, active=True)
        db.session.add(user1)
    
    if not user2:
        user2 = User(email="user2@example.com", password="password2", created_at=datetime.utcnow(), email_confirmed=False, active=True)
        db.session.add(user2)
    
    db.session.commit()

    # Check if user details already exist
    user_details1 = UserDetails.query.filter_by(user_id=user1.id).first()
    user_details2 = UserDetails.query.filter_by(user_id=user2.id).first()

    if not user_details1:
        user_details1 = UserDetails(user_id=user1.id, age=25, gender="M", height=175.5, weight=70, kcal_goal=2500, fat_goal=70, protein_goal=150, carb_goal=300)
        db.session.add(user_details1)
    
    if not user_details2:
        user_details2 = UserDetails(user_id=user2.id, age=30, gender="F", height=160.0, weight=55, kcal_goal=2000, fat_goal=60, protein_goal=100, carb_goal=250)
        db.session.add(user_details2)
    
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

    # Tworzenie posiłków
    meal1 = Meal(name="Keto Breakfast", description="Eggs and avocado", category_id=category1.id, diet_id=diet1.id)
    meal2 = Meal(name="Vegan Lunch", description="Quinoa salad", category_id=category2.id, diet_id=diet2.id)

    db.session.add_all([meal1, meal2])
    db.session.commit()

    print("Database seeded successfully.")
