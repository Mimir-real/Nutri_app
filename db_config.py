import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def db_create_all():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Tworzenie tabel na podstawie modeli
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id SERIAL PRIMARY KEY,
            product_name VARCHAR(255),
            generic_name VARCHAR(255),
            kcal_100g FLOAT,
            protein_100g FLOAT,
            carbs_100g FLOAT,
            fat_100g FLOAT,
            brand VARCHAR(255),
            barcode VARCHAR(255),
            image_url VARCHAR(255),
            labels_tags VARCHAR(255),
            product_quantity FLOAT,
            allergens VARCHAR(255),
            tsv TSVECTOR
        );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS tsv_idx ON ingredients USING gin(tsv);')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            email VARCHAR(128) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP,
            email_confirmed BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT TRUE
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            user_id INTEGER PRIMARY KEY REFERENCES "user"(id),
            age SMALLINT,
            gender VARCHAR(1),
            height FLOAT,
            weight FLOAT,
            kcal_goal SMALLINT,
            fat_goal SMALLINT,
            protein_goal SMALLINT,
            carb_goal SMALLINT
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id),
            code VARCHAR(128),
            type_id INTEGER REFERENCES link_types(id),
            used BOOLEAN DEFAULT FALSE,
            expire_at TIMESTAMP
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS link_types (
            id SERIAL PRIMARY KEY,
            type VARCHAR(32)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diet (
            id SERIAL PRIMARY KEY,
            name VARCHAR(64),
            description TEXT
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_diets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(id),
            diet_id INTEGER NOT NULL REFERENCES diet(id),
            allowed BOOLEAN DEFAULT TRUE,
            CONSTRAINT _user_diet_uc UNIQUE (user_id, diet_id)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            description VARCHAR(255),
            creator_id INTEGER REFERENCES "user"(id),
            diet_id INTEGER REFERENCES diet(id),
            category_id INTEGER REFERENCES meal_category(id),
            version INTEGER,
            last_update TIMESTAMP
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_category (
            id SERIAL PRIMARY KEY,
            category VARCHAR(32),
            description VARCHAR(255)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_ingredients (
            id SERIAL PRIMARY KEY,
            meal_id INTEGER REFERENCES meal(id),
            ingredient_id INTEGER REFERENCES ingredients(id),
            unit VARCHAR(255),
            quantity FLOAT,
            CONSTRAINT _meal_ingredient_uc UNIQUE (meal_id, ingredient_id)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_history (
            id SERIAL PRIMARY KEY,
            composition JSON,
            meal_id INTEGER REFERENCES meal(id),
            meal_version INTEGER
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_schedule (
            id SERIAL PRIMARY KEY,
            meal_history_id INTEGER REFERENCES meal_history(id),
            at TIMESTAMP,
            user_id INTEGER REFERENCES "user"(id)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_log (
            id SERIAL PRIMARY KEY,
            meal_history_id INTEGER REFERENCES meal_history(id),
            portion FLOAT,
            at TIMESTAMP,
            user_id INTEGER REFERENCES "user"(id)
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()