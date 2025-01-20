from datetime import datetime
from models import db, User, UserDetails, Diet, UserDiets, MealCategory, Meal, LinkTypes

def seed_database():
    # Tworzenie linków
    link_type_activate = LinkTypes.query.filter_by(type="activate").first()
    link_type_restore = LinkTypes.query.filter_by(type="restore").first()

    if not link_type_activate:
        print("Creating link type 'activate'")
        link_type_activate = LinkTypes(type="activate")
        db.session.add(link_type_activate)
    if not link_type_restore:
        print("Creating link type 'restore'")
        link_type_restore = LinkTypes(type="restore")
        db.session.add(link_type_restore)
    db.session.commit()

    # Tworzenie diet
    diet_normal = Diet.query.filter_by(name="Normal").first()
    diet_keto = Diet.query.filter_by(name="Keto").first()
    diet_vegan = Diet.query.filter_by(name="Vegan").first()

    if not diet_normal:
        print("Creating diet 'Normal'")
        diet_normal = Diet(name="Normal", description="Balanced diet.")
        db.session.add(diet_normal)
    if not diet_keto:
        print("Creating diet 'Keto'")
        diet_keto = Diet(name="Keto", description="Low-carb, high-fat diet.")
        db.session.add(diet_keto)
    if not diet_vegan:
        print("Creating diet 'Vegan'")
        diet_vegan = Diet(name="Vegan", description="Plant-based diet without animal products.")
        db.session.add(diet_vegan)
    db.session.commit()

    # # Tworzenie kategorii posiłków
    category_breakfast = MealCategory.query.filter_by(category="Breakfast").first()
    if not category_breakfast:
        print("Creating meal category 'Breakfast'")
        category_breakfast = MealCategory(category="Breakfast", description="Morning meal")
        db.session.add(category_breakfast)
    category_lunch = MealCategory.query.filter_by(category="Lunch").first()
    if not category_lunch:
        print("Creating meal category 'Lunch'")
        category_lunch = MealCategory(category="Lunch", description="Midday meal")
        db.session.add(category_lunch)
    category_dinner = MealCategory.query.filter_by(category="Dinner").first()
    if not category_dinner:
        print("Creating meal category 'Dinner'")
        category_dinner = MealCategory(category="Dinner", description="Evening meal")
        db.session.add(category_dinner)
    category_snack = MealCategory.query.filter_by(category="Snack").first()
    if not category_snack:
        print("Creating meal category 'Snack'")
        category_snack = MealCategory(category="Snack", description="Between meals")
        db.session.add(category_snack)
    db.session.commit()

    print("Database seeded successfully.")
