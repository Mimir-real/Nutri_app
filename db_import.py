import csv
import gzip
import sys
from models import db, Ingredients

csv.field_size_limit(sys.maxsize)


# https://openfoodfacts-ds.s3.eu-west-3.amazonaws.com/en.openfoodfacts.org.products.csv.gz
def import_database():
    with gzip.open('en.openfoodfacts.org.products.csv.gz', 'rt') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        i = 0
        for p in reader:
            product = Ingredients(
                product_name = p['product_name'],
                generic_name = p['generic_name'],
                kcal_100g = p['energy-kcal_100g'] or None,
                protein_100g = p['proteins_100g'] or None,
                carbs_100g = p['carbohydrates_100g'] or None,
                fat_100g = p['fat_100g'] or None,
                brand = p['brands'],
                barcode = p['code'],
                image_url = p['image_url'],
                labels_tags = p['labels_tags'],
                product_quantity = p['product_quantity'] or None,
                allergens = p['allergens']
            )
            db.session.add(product)
            i += 1
            # commit every 100 000 records to reduce memory usage and speed up things
            if i % 100_000 == 0:
                db.session.commit()
        db.session.commit()

