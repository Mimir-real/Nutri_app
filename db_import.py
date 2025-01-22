import csv
import gzip
import psycopg2
from db_config import get_db_connection
from psycopg2.extras import RealDictCursor

csv.field_size_limit(2**31 - 1)

def import_database():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    with gzip.open('en.openfoodfacts.org.products.csv.gz', 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        i = 0
        for p in reader:
            cursor.execute('''
                INSERT INTO ingredients (
                    product_name, generic_name, kcal_100g, protein_100g, carbs_100g, fat_100g, brand, barcode, image_url, labels_tags, product_quantity, allergens
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                p['product_name'],
                p['generic_name'],
                p['energy-kcal_100g'] or None,
                p['proteins_100g'] or None,
                p['carbohydrates_100g'] or None,
                p['fat_100g'] or None,
                p['brands'],
                p['code'],
                p['image_url'],
                p['labels_tags'],
                p['product_quantity'] or None,
                p['allergens']
            ))
            i += 1
            # commit every 100 000 records to reduce memory usage and speed up things
            if i % 100_000 == 0:
                conn.commit()
        conn.commit()

    cursor.close()
    conn.close()