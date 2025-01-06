import csv
import gzip
import sys
from models import db, Ingredients

csv.field_size_limit(sys.maxsize)


# https://openfoodfacts-ds.s3.eu-west-3.amazonaws.com/en.openfoodfacts.org.products.csv.gz
def import_database():
    with gzip.open('en.openfoodfacts.org.products.csv.gz', 'rt') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for p in reader:
            product = Ingredients(
                product_name = p['product_name'],
                generic_name = p['generic_name'],
                kcal_100g = p['energy-kcal_100g'],
                protein_100g = p['proteins_100g'],
                carbs_100g = p['carbohydrates_100g'],
                fat_100g = p['fat_100g'],
                brand = p['brands'],
                barcode = p['code'],
                image_url = p['image_url'],
                labels_tags = p['labels_tags'],
                product_quantity = p['product_quantity'],
                allergens = p['allergens']
            )
            db.session.add(product)
        db.session.commit()
