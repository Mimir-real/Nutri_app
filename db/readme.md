# **Backup.dump** - Opis zawartości

## Tablice ogólne

   Tablice ogólne w bazie danych służą do przechowywania podstawowych informacji, które są wykorzystywane w różnych częściach aplikacji. 

### Link_types

   Tabela `link_types` zawiera typy linków, które mogą być wygenerowane do potwierdzenia emaila bądź resetowania hasła użytkownika.

   ```bash
   SELECT * FROM link_types;
   id |   type   
   ---+----------
   1  | activate
   2  | restore
   ```

### Diet

   Tabela `diet` zawiera typy diet, które mogą być przypisane do tworzonych posiłków

   ```bash
   SELECT * FROM diet;
    id |  name  |                description                
   ----+--------+-------------------------------------------
     1 | Normal | Balanced diet.
     2 | Keto   | Low-carb, high-fat diet.
     3 | Vegan  | Plant-based diet without animal products.
   ```

### Meal_category

   Tabela `meal_category` zawiera kategorię posiłków, którą można przypisać do tworzonych posiłków

   ```bash
   SELECT * FROM meal_category;
    id | category  |  description  
   ----+-----------+---------------
     1 | Breakfast | Morning meal
     2 | Lunch     | Midday meal
     3 | Dinner    | Evening meal
     4 | Snack     | Between meals
   ```

### Ingredients

   ```bash
   SELECT * FROM ingredients WHERE product_quantity is not null LIMIT 3;
      id   |      product_name      | generic_name |    kcal_100g    |  protein_100g  |   carbs_100g    |    fat_100g     |      brand      |    barcode    |                                      image_url                                       |                    labels_tags                    | product_quantity | allergens |                tsv                 
   --------+------------------------+--------------+-----------------+----------------+-----------------+-----------------+-----------------+---------------+--------------------------------------------------------------------------------------+---------------------------------------------------+------------------+-----------+------------------------------------
    121603 | Lentil salad           |              |             170 |              9 |              23 |               6 |                 | 0030831001143 | https://images.openfoodfacts.org/images/products/003/083/100/1143/front_fr.3.400.jpg |                                                   |     283.49523125 |           | 'lentil':1 'salad':2
    121606 | Burrito Tortillas      |              | 313.72549019608 | 7.843137254902 | 52.941176470588 | 6.8627450980392 |                 | 0030832424644 | https://images.openfoodfacts.org/images/products/003/083/242/4644/front_en.3.400.jpg |                                                   |     623.68950875 |           | 'burrito':1 'tortilla':2
    121611 | Plant kitchen coleslaw |              |             236 |              1 | 5.0999999046326 |  23.10000038147 | Marks & Spencer | 00308441      | https://images.openfoodfacts.org/images/products/000/000/030/8441/front_en.3.400.jpg | en:vegetarian,en:vegan,en:green-dot,en:new-recipe |              300 |           | 'coleslaw':3 'kitchen':2 'plant':1
   ```

## Tablice użytkowe

    Tablice użytkowe, (do uzupelnienia)

### Users

   Tabela `users` zawiera:

   1. Aktywnego użykownika (ID=14) z potwierdzonym emailem:
      - Login: `normalny@user.pl`
      - Hasło: `trudne_haslo`

   2. Nieaktywowanego użytkownika (ID=17) - brak potwierdzenia po rejestracji, zarejestrował się pare dni temu
      - Login: `przeterminowany@user.pl`
      - Haslo: `trudne_haslo`
      - Kod aktywacyjny: `b2f4048f-6454-4434-81d1-ba1bf6207550`

   3. Dezaktywowanego użytkownika (ID=18) - został zarejestrowany oraz dezaktywowany (przeznaczony do usunięcia w przyszłości)
      - Login: `dezaktywowany@user.pl`
      - Haslo: `trudne_haslo`

### Links

   Tabela `links` zawiera jedynie link aktywacyjny dla użytkownika, który rejestrował się pare dni temu i nie aktywował swojego konta.

   ```bash
   SELECT * FROM links;
    id | user_id |                 code                 | type_id | used |         expire_at          
   ----+---------+--------------------------------------+---------+------+----------------------------
    15 |      17 | b2f4048f-6454-4434-81d1-ba1bf6207550 |       1 | f    | 2025-01-22 16:10:08.023197
   ```

### User_details

   Tabela `user_details` przechowuje cele kaloryczne użytkowników oraz podstawowe informacje o nich, takie jak płeć _(X/M/F)_, wzrost, waga czy wiek.

   ```bash
   SELECT * FROM user_details;
    user_id | age | gender | height | weight | kcal_goal | fat_goal | protein_goal | carb_goal 
   ---------+-----+--------+--------+--------+-----------+----------+--------------+-----------
         14 |  21 | X      |  184.3 |   83.6 |      2100 |       50 |           70 |       400
   ```

### User_diets

   Tabela `user_diets` przechowuje informacje o dozwolonych i niedozwolonych dietach dla poszczególnych użytkowników. Te ograniczenia są wykorzystywane przy szukaniu posiłków.

   ```bash
   SELECT * FROM user_diets;
    id | user_id | diet_id | allowed 
   ----+---------+---------+---------
    11 |      14 |       3 | t
    12 |      14 |       2 | f
    13 |      18 |       3 | f
   ```

### Meal

   Tabela `meal` zawiera posiłki stworzone przez użytkowników oraz ich szczegóły (dieta, kategoria).

   Dodatkowo każdy rekord zawiera wersję posiłku oraz timestamp ostatniej aktualizacji

   Baza przed aktualizacją:
   ```bash
   SELECT * FROM meal WHERE id = 14;
    id |       name       | description | creator_id | diet_id | category_id | version |        last_update         
   ----+------------------+-------------+------------+---------+-------------+---------+----------------------------
    14 | Płatki z mlekiem |             |         14 |       1 |           1 |       1 | 2025-01-26 16:38:00.094739
   ```

   Baza po aktualizacji:
   ```bash
   SELECT * FROM meal WHERE id = 14;
    id |       name       |  description   | creator_id | diet_id | category_id | version |        last_update        
   ----+------------------+----------------+------------+---------+-------------+---------+---------------------------
    14 | Mleko z płatkami | Najpierw mleko |         14 |       1 |           1 |       2 | 2025-01-26 16:38:56.21142
   ```

   Pełny aktualny stan bazy:
   ```bash
   SELECT * FROM meal;
    id |       name       |  description   | creator_id | diet_id | category_id | version |        last_update         
   ----+------------------+----------------+------------+---------+-------------+---------+----------------------------
    14 | Mleko z płatkami | Najpierw mleko |         14 |       1 |           1 |       2 | 2025-01-26 16:38:56.21142
    16 | Coś Wege         | Ujdzie         |         14 |       3 |           4 |       1 | 2025-01-26 17:01:57.300402
    17 | Mielone z ryżem  | Spoko obiad    |         18 |       1 |           3 |       1 | 2025-01-26 17:04:23.282463
   ```

### Meal_ingredients

   Tabela `meal_ingredients` zawiera ...

   ```bash
   SELECT * FROM meal_ingredients;
    id | meal_id | ingredient_id | unit | quantity 
   ----+---------+---------------+------+----------
    23 |      14 |        114368 | g    |      100
    24 |      14 |       1072345 | g    |      250
    27 |      16 |           180 | g    |      150
    28 |      17 |       1030437 | g    |      500
    29 |      17 |       1283820 | g    |     1000
   ```

### Meal_history

   Tabela `meal_history` zawiera ...

   ```bash
   SELECT * FROM meal_history;
    id |                                                                                                             composition                                                                                                              | meal_id | meal_version 
   ----+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+--------------
    32 | {"name": "P\u0142atki z mlekiem", "diet_id": 1, "category_id": 1, "ingredients": [{"ingredient_id": 114368, "unit": "g", "quantity": 100}, {"ingredient_id": 1072345, "unit": "g", "quantity": 250}]}                                |      14 |            1
    33 | {"id": 14, "name": "P\u0142atki z mlekiem", "description": "", "creator_id": 14, "diet_id": 1, "category_id": 1, "version": 1, "last_update": "2025-01-26T16:38:00.094739"}                                                          |      14 |            1
    35 | {"name": "Co\u015b Wege", "description": "Ujdzie", "diet_id": 3, "category_id": 4, "ingredients": [{"ingredient_id": 180, "unit": "g", "quantity": 150}]}                                                                            |      16 |            1
    36 | {"name": "Mielone z ry\u017cem", "description": "Spoko obiad", "diet_id": 1, "category_id": 3, "ingredients": [{"ingredient_id": 1030437, "unit": "g", "quantity": 500}, {"ingredient_id": 1283820, "unit": "g", "quantity": 1000}]} |      17 |            1
   ```

### Food_schedule

   Tabela `food_schedule` zawiera ... 

   ```bash

   ```

### Food_Log

   Tabela `food_log` zawiera ... 

   ```bash

   ```