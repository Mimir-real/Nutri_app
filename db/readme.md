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