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

   Tablice użytkowe przechowują informacje specyficzne dla użytkowników, takie jak dane logowania, preferencje dietetyczne, zaplanowane posiłki i zjedzone posiłki.

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

   4. Drugiego aktywnego użykownika (ID=14) z potwierdzonym emailem:
      - Login: `normalny2@user.pl`
      - Hasło: `trudne_haslo`

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
         19 |  21 | X      |  184.3 |   83.6 |      2100 |       50 |           70 |       400
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
   SELECT * FROM meal WHERE id = 27;
    id |       name       |  description   | creator_id | diet_id | category_id | version |        last_update         
   ----+------------------+----------------+------------+---------+-------------+---------+----------------------------
    27 | Płatki z mlekiem | Najpierw mleko |         14 |       1 |           1 |       1 | 2025-01-26T18:51:00.563404
   ```

   Baza po aktualizacji:
   ```bash
   SELECT * FROM meal WHERE id = 27;
    id |       name       |  description   | creator_id | diet_id | category_id | version |        last_update         
   ----+------------------+----------------+------------+---------+-------------+---------+----------------------------
    27 | Płatki z mlekiem | Najpierw mleko |         14 |       1 |           1 |       2 | 2025-01-26 18:51:26.939319
   ```

   Pełny aktualny stan bazy:
   ```bash
   SELECT * FROM meal;
    id |       name       |  description   | creator_id | diet_id | category_id | version |        last_update         
   ----+------------------+----------------+------------+---------+-------------+---------+----------------------------
    27 | Płatki z mlekiem | Najpierw mleko |         14 |       1 |           1 |       2 | 2025-01-26 18:51:26.939319
    28 | Coś Wege         |                |         14 |       3 |           4 |       1 | 2025-01-26 18:51:39.404197
    29 | Mielone z ryżem  | Spoko obiad    |         19 |       1 |           3 |       1 | 2025-01-26 18:55:18.678454
   ```

### Meal_ingredients

   Tabela `meal_ingredients` zawiera składniki przypisane do posiłków, w tym ich jednostki miary oraz ilości.

   ```bash
   SELECT * FROM meal_ingredients;
    id | meal_id | ingredient_id | unit | quantity 
   ----+---------+---------------+------+----------
    48 |      27 |       1033381 | g    |      250
    49 |      27 |        114368 | g    |      100
    50 |      28 |          8062 | g    |      200
    51 |      29 |       1030437 | g    |      500
    52 |      29 |       1283820 | g    |      250
   ```

### Meal_history

   Tabela `meal_history` przechowuje historię zmian posiłków, w tym ich skład oraz wersje.

   
   ```bash
   SELECT * FROM meal_history;
    id |                                                                                                                  composition                                                                                                                   | meal_id | meal_version 
   ----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+--------------
    60 | {"meal": {"diet_id": 1, "category_id": 1, "last_update": "2025-01-26T18:51:00.563404", "version": 1}, "ingredients": [{"ingredient_id": 114368, "unit": "g", "quantity": 150.0}, {"ingredient_id": 1033381, "unit": "g", "quantity": 300.0}]}  |      27 |            1
    61 | {"meal": {"diet_id": 1, "category_id": 1, "last_update": "2025-01-26T18:51:26.939319", "version": 2}, "ingredients": [{"ingredient_id": 114368, "unit": "g", "quantity": 100.0}, {"ingredient_id": 1033381, "unit": "g", "quantity": 250.0}]}  |      27 |            2
    62 | {"meal": {"diet_id": 3, "category_id": 4, "last_update": "2025-01-26T18:51:39.404197", "version": 1}, "ingredients": [{"ingredient_id": 8062, "unit": "g", "quantity": 200.0}]}                                                                |      28 |            1
    63 | {"meal": {"diet_id": 1, "category_id": 3, "last_update": "2025-01-26T18:55:18.678454", "version": 1}, "ingredients": [{"ingredient_id": 1030437, "unit": "g", "quantity": 500.0}, {"ingredient_id": 1283820, "unit": "g", "quantity": 250.0}]} |      29 |            1
   ```

### Food_schedule

   Tabela `food_schedule` przechowuje zaplanowane posiłki użytkowników, w tym identyfikator historii posiłku, datę i godzinę oraz identyfikator użytkownika.

   ```bash
   SELECT * FROM food_schedule;
    id | meal_history_id |         at          | user_id 
   ----+-----------------+---------------------+---------
    21 |              60 | 2025-02-01 20:00:00 |      19
    22 |              60 | 2025-02-02 20:00:00 |      19
    24 |              61 | 2025-02-02 08:00:00 |      19
    25 |              63 | 2025-02-03 19:00:00 |      19
    26 |              62 | 2025-02-05 19:00:00 |      19
   ```

### Food_Log

   Tabela `food_log` przechowuje zjedzone posiłki użytkowników, w tym identyfikator historii posiłku, porcję, datę i godzinę oraz identyfikator użytkownika.

   ```bash
   SELECT * FROM food_log;
    id | meal_history_id | portion |         at          | user_id 
   ----+-----------------+---------+---------------------+---------
    14 |              61 |     300 | 2025-01-20 01:49:06 |      19
    15 |              63 |     200 | 2025-01-20 22:18:06 |      19
    16 |              62 |     500 | 2025-01-21 19:24:28 |      19
    17 |              60 |     500 | 2025-01-23 10:10:12 |      19
   ```

   