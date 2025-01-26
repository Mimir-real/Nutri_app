## endpoints/auth.py
Funkcje odpowiedzialne za logowanie, weryfikację tożsamości użytkowników oraz zarządzanie dostępem do zasobów w aplikacji Flask.
- Hasła użytkowników są przechowywane jako hashe przy użyciu `generate_password_hash` z biblioteki Werkzeug.
- Autoryzacja i dostęp do zasobów są zabezpieczone tokenami JWT.
- Obsługa błędów zapewnia, że brakujące dane lub nieprawidłowe żądania zwracają odpowiednie komunikaty dla klienta.

---


### `login()`
Obsługuje logowanie użytkownika do systemu. Weryfikuje poświadczenia, generuje token dostępu (JWT) i zwraca go do klienta.

**Endpoint:**
`POST /login`

**Parametry wejściowe:**
Przyjmuje dane w formacie JSON w ciele żądania:
- `email` (string) – Email użytkownika (wymagane).
- `password` (string) – Hasło użytkownika (wymagane).

**Odpowiedzi:**
- **200:** Logowanie zakończone sukcesem. Zwracany jest token dostępu.
- **400:** Nieprawidłowe żądanie – brakujące dane.
- **401:** Logowanie nieudane – nieprawidłowe poświadczenia.


---

### `get_logged_user()`
Zwraca dane zalogowanego użytkownika na podstawie tokena JWT.

**Endpoint:**
`GET /user/me`

**Wymagania:**
Autoryzacja za pomocą tokena JWT (nagłówek `Authorization`).

**Odpowiedzi:**
- **200:** Informacje o użytkowniku: id, email, czy email jest potwierdzony, czy użytkownik jest aktywny, kiedy został utworzony.

- **403:** Kod błędu "brak autoryzacji".

---

### `login_required(fn, optional_message)`
Dekorator sprawdzający, czy użytkownik jest zalogowany i czy jego konto jest aktywne.

**Argumenty:**
- `fn` – Funkcja, która zostanie opakowana przez dekorator.
- `optional_message` (string) – Opcjonalna wiadomość wyświetlana w przypadku braku autoryzacji (domyślnie: "You must be logged in to access this resource").

**Działanie:**
Jeśli użytkownik jest nieaktywny lub niezalogowany, funkcja zwraca odpowiedź unauthrorized.


---

### `anonymous_required(fn, optional_message)`
Dekorator zapewniający, że dostęp do zasobu mają tylko użytkownicy niezalogowani.

**Argumenty:**
- `fn` – Funkcja, która zostanie opakowana przez dekorator.
- `optional_message` (string) – Opcjonalna wiadomość wyświetlana w przypadku, gdy użytkownik jest zalogowany (domyślnie: "You must be logged out to access this resource").

**Działanie:**
Jeśli użytkownik jest zalogowany, funkcja zwraca odpowiedni błąd.


---

### `verify_identity(user_id, optional_message)`
Weryfikuje, czy zalogowany użytkownik jest właścicielem określonych zasobów na podstawie porównania identyfikatorów.

**Argumenty:**
- `user_id` (int) – Identyfikator użytkownika, który ma być zweryfikowany.
- `optional_message` (string) – Opcjonalna wiadomość wyświetlana w przypadku nieautoryzowanego dostępu (domyślnie: "You can't perform this action").

**Działanie:**
Jeśli `user_id` nie jest zgodne z tożsamością użytkownika z tokena JWT, funkcja zwraca odpowiedź unauthorized:

---

## endpoints/user_details.py  
Funkcja odpowiedzialna za tworzenie szczegółowych danych użytkownika.  

- Wymagana autoryzacja za pomocą tokena JWT.  
- Zapewnia weryfikację tożsamości, aby użytkownicy mogli tworzyć szczegóły tylko dla siebie.  
- Walidacja danych wejściowych oraz odpowiednie komunikaty zwrotne w przypadku błędów.  

---

### `create_user_details(user_id)`  
Tworzy szczegóły użytkownika dla określonego `user_id`.

**Endpoint:**  
`POST /user/{user_id}/details`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  
- Dane w formacie JSON w ciele żądania:  

| Pole             | Typ     | Opis                                           |
|-------------------|---------|------------------------------------------------|
| `age`            | integer | Wiek użytkownika (wymagane).                   |
| `gender`         | string  | Płeć użytkownika: `F`, `M`, `X` (wymagane).    |
| `height`         | number  | Wzrost użytkownika (wymagane).                 |
| `weight`         | number  | Waga użytkownika (wymagane).                   |
| `kcal_goal`      | integer | Dzienny cel kaloryczny użytkownika (wymagane). |
| `fat_goal`       | integer | Dzienny cel tłuszczu (w gramach, wymagane).    |
| `protein_goal`   | integer | Dzienny cel białka (w gramach, wymagane).      |
| `carb_goal`      | integer | Dzienny cel węglowodanów (w gramach, wymagane).|

**Walidacja:**  
- Weryfikacja, czy użytkownik istnieje oraz czy szczegóły użytkownika już nie istnieją.  
- Walidacja płci (`gender`) – akceptowane wartości: `F`, `M`, `X`.  
- Sprawdzenie, czy wszystkie wartości liczbowe są większe lub równe 0.  

**Odpowiedzi:**  
- **201:** Szczegóły użytkownika utworzone pomyślnie.  
  ```json
  {
    "message": "User details created successfully"
  }
  ```
- **400:** Błąd walidacji – np. brakujące dane, nieprawidłowa płeć, szczegóły użytkownika już istnieją.  
  ```json
  {
    "error": "User details already exist"
  }
  ```
- **404:** Użytkownik o podanym `user_id` nie istnieje.  
  ```json
  {
    "message": "User not found"
  }
  ```
- **500:** Wewnętrzny błąd serwera.  
  ```json
  {
    "error": "Internal server error"
  }
  ```

---

### Działanie funkcji  
1. **Weryfikacja tożsamości:** Funkcja sprawdza, czy użytkownik jest autoryzowany do utworzenia szczegółów tylko dla swojego konta.  
2. **Walidacja wejścia:** Weryfikowane są wartości pól JSON oraz `user_id`.  
3. **Operacje na bazie danych:**  
   - Sprawdzenie istnienia użytkownika w tabeli `user`.  
   - Sprawdzenie, czy szczegóły użytkownika już istnieją w tabeli `user_details`.  
   - Dodanie nowych szczegółów do tabeli `user_details`.  
4. **Zwracanie odpowiedzi:** Funkcja zwraca odpowiedni status oraz komunikat w zależności od wyniku operacji.

---


### `update_user_details(user_id)`
Obsługuje aktualizację szczegółów użytkownika w systemie. Aktualizuje dane osobowe oraz cele żywieniowe w bazie danych.

**Endpoint:**
`PUT /user_details/<user_id>`

**Parametry wejściowe:**
- `user_id` (integer) – ID użytkownika, którego dane mają zostać zaktualizowane (parametr ścieżki, wymagany).

Przyjmuje dane w formacie JSON w ciele żądania:
- `age` (integer) – Wiek użytkownika (opcjonalne).
- `gender` (string) – Płeć użytkownika (opcjonalne; dozwolone wartości: `F`, `M`, `X`).
- `height` (number) – Wzrost użytkownika (opcjonalne).
- `weight` (number) – Waga użytkownika (opcjonalne).
- `kcal_goal` (integer) – Dzienny cel kaloryczny użytkownika (opcjonalne).
- `fat_goal` (integer) – Dzienny cel spożycia tłuszczu (opcjonalne).
- `protein_goal` (integer) – Dzienny cel spożycia białka (opcjonalne).
- `carb_goal` (integer) – Dzienny cel spożycia węglowodanów (opcjonalne).

**Odpowiedzi:**
- **200:** Aktualizacja zakończona sukcesem. Zwracany jest komunikat o powodzeniu.
  ```json
  {
    "message": "User details updated successfully"
  }
  ```
- **400:** Nieprawidłowe żądanie – brakujące dane lub nieprawidłowe wartości.
  ```json
  {
    "error": "Invalid gender value"
  }
  ```
- **404:** Nie znaleziono użytkownika lub szczegółów użytkownika.
  ```json
  {
    "message": "User details not found"
  }
  ```
- **500:** Wewnętrzny błąd serwera.
  ```json
  {
    "error": "Internal server error"
  }
  ```

**Działanie:**
1. Weryfikacja tożsamości użytkownika za pomocą funkcji `verify_identity`.
2. Pobranie danych z żądania i walidacja wartości (np. sprawdzenie płci, czy wartości są dodatnie).
3. Sprawdzenie, czy użytkownik i jego szczegóły istnieją w bazie danych.
4. Aktualizacja szczegółów użytkownika w tabeli `user_details`.
5. Zwrócenie odpowiedniej odpowiedzi w zależności od wyniku operacji.

---


### `get_user_details(user_id)`  
Pobiera szczegóły użytkownika dla określonego `user_id`.

**Endpoint:**  
`GET /user/{user_id}/details`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  

**Walidacja:**  
- Weryfikacja, czy użytkownik istnieje.  
- Sprawdzenie, czy szczegóły użytkownika istnieją w bazie danych.  

**Odpowiedzi:**  
- **200:** Szczegóły użytkownika pobrane pomyślnie.  
  ```json
  {
    "user_id": 1,
    "age": 25,
    "gender": "M",
    "height": 180.5,
    "weight": 75.0,
    "kcal_goal": 2000,
    "fat_goal": 70,
    "protein_goal": 150,
    "carb_goal": 250
  }
- **400** błąd walidacji, np. brakujące user_id. 
- **404** brak użytkownika o podanym user_id.
- **500** wewnętrzny błąd serwera

---
## endpoints/user_diets.py  
Funkcja odpowiedzialna za przypisywanie diety do użytkownika.  

- Wymagana autoryzacja za pomocą tokena JWT.  
- Zapewnia weryfikację tożsamości, aby użytkownicy mogli przypisywać diety tylko dla siebie.  
- Walidacja danych wejściowych oraz odpowiednie komunikaty zwrotne w przypadku błędów.  

---

### `assign_diet_to_user(user_id)`  
Przypisuje dietę do użytkownika o określonym `user_id`.

**Endpoint:**  
`POST /user/{user_id}/diets`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  
- Dane w formacie JSON w ciele żądania:  

| Pole        | Typ      | Opis                                                                 |
|-------------|----------|----------------------------------------------------------------------|
| `diet_id`   | integer  | ID diety do przypisania (wymagane).                                  |
| `allowed`   | boolean  | Określa, czy dieta jest dozwona dla użytkownika (domyślnie: `true`). |

**Walidacja:**  
- Sprawdzenie istnienia użytkownika i diety w bazie danych.  
- Weryfikacja, czy dieta nie jest już przypisana do użytkownika.  
- Walidacja wymaganych pól (`diet_id`).  

**Odpowiedzi:**  

- **201:** Dieta przypisana pomyślnie.  
  ```json
  {
    "message": "Diet assigned to user"
  }
  ```
  
- **400:** Błąd walidacji np. brakujące diet_id.
  ```json
  {
    "error": "diet_id is required"
  }  
  ```

  - **404:** Użytkownik nie istnieje.
  ```json
  {
    "message": "User not found"
  }
  ```

    - **500:** Wewnętrzny błąd serwera.
  ```json
  {
    "error": "Internal server error"
  }
  ```

  ---
### `remove_diet_from_user(user_id, diet_id)`  
Usuwa przypisaną dietę użytkownikowi o określonym `user_id`.

**Endpoint:**  
`DELETE /user/{user_id}/diets/{diet_id}`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  
- `diet_id` (integer) – ID diety do usunięcia (parametr ścieżki, wymagany).  

**Walidacja:**  
- Sprawdzenie, czy dieta jest przypisana do użytkownika w tabeli `user_diets`.  

**Odpowiedzi:**  
- **200:** Dieta usunięta pomyślnie.  
  ```json
  {
    "message": "Diet removed from user"
  }
  ```
  ---
  
### `get_user_diets(user_id)`  
Pobiera listę diet przypisanych do użytkownika o określonym `user_id`.

**Endpoint:**  
`GET /user/{user_id}/diets`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  

**Walidacja:**  
- Weryfikacja autoryzacji użytkownika.  

**Odpowiedzi:**  
- **200:** Pomyślnie zwrócono listę diet użytkownika.  
  ```json
  [
    {
      "user_id": 1,
      "diet_id": 5,
      "allowed": true
    },
    {
      "user_id": 1,
      "diet_id": 8,
      "allowed": false
    }
  ]
  ```

  ---

  ## endpoints/users.py
  Funkcje odpowiedzialne za pobieranie obecnie zalogowanego użytkownika (siebie), tworzenie użytkonwika, pobieranie listy określonej liczby użytkowników, pobieranie konkretnego użytkownika, aktywację konta użytkownika, deaktywację użytkownika

  ---

### `get_me()`  
Pobiera informacje o aktualnie zalogowanym użytkowniku.

**Endpoint:**  
`GET /users/me`

**Parametry wejściowe:**  
*Brak parametrów ścieżki lub zapytania.*  

**Walidacja:**  
- Automatyczna weryfikacja tokena JWT przez dekorator `@login_required`.  

**Odpowiedzi:**  
- **200:** Pomyślnie zwrócono dane użytkownika.  
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "email_confirmed": true,
    "active": true,
    "created_at": "2023-01-01T12:00:00Z"
  }
  ```
- **401:** Brak autoryzacji
  ```json
  {
  "error": "Unauthorized"
  }
  ```
- **403:** Błąd dostępu
  ```json
  {
  "error": "Access denied"
  }
  ```
- **500:** Wewnętrzny błąd serwera
  ```json
  {
  "error": "Unauthorized"
  }
  ```
  ---
  
### `create_user()`  
Tworzy nowego użytkownika w systemie.

**Endpoint:**  
`POST /users`

**Parametry wejściowe:**  
- Dane w formacie JSON w ciele żądania:  

| Pole                 | Typ      | Opis                                     |
|-----------------------|----------|------------------------------------------|
| `email`              | string   | Adres email użytkownika (wymagane).      |
| `password`           | string   | Hasło użytkownika (wymagane).            |
| `confirm_password`   | string   | Potwierdzenie hasła (wymagane).          |

**Walidacja:**  
- Wszystkie pola muszą być podane.  
- Hasło i potwierdzenie hasła muszą być identyczne.  
- Email musi być unikalny (nie może istnieć w bazie).  

**Odpowiedzi:**  
- **201:** Użytkownik utworzony pomyślnie.  
  ```json
  {
    "message": "User created",
    "user_id": 5,
    "activation_code": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
  }
  ```

  ---

  ### `get_users()`  
Pobiera listę użytkowników z możliwością stronicowania.

**Endpoint:**  
`GET /users`

**Parametry wejściowe (query):**  
| Pole       | Typ      | Opis                                      | Domyślna wartość |
|------------|----------|-------------------------------------------|------------------|
| `limit`    | integer  | Liczba użytkowników na stronie.           | 10               |
| `page`     | integer  | Numer strony.                             | 1                |

**Walidacja:**  
- `limit` i `page` muszą być liczbami całkowitymi większymi od 0.  

**Odpowiedzi:**  
- **200:** Pomyślnie zwrócono listę użytkowników.  
  ```json
  {
    "users": [
      {
        "id": 1,
        "email": "user1@example.com",
        "email_confirmed": true,
        "active": true,
        "created_at": "2023-01-01T12:00:00Z"
      },
      {
        "id": 2,
        "email": "user2@example.com",
        "email_confirmed": false,
        "active": false,
        "created_at": "2023-01-02T12:00:00Z"
      }
    ],
    "total": 50,
    "pages": 5,
    "current_page": 1,
    "page_size": 10
  }
  ```

  ---

### `get_user(user_id)`  
Pobiera szczegóły konta użytkownika o określonym `user_id`.

**Endpoint:**  
`GET /users/{user_id}`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  

**Walidacja:**  
- Sprawdzenie istnienia użytkownika w bazie danych.  

**Odpowiedzi:**  
- **200:** Pomyślnie zwrócono dane użytkownika.  
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "email_confirmed": true,
    "active": true,
    "created_at": "2023-01-01T12:00:00Z"
  }
  ```

  ---

  ### `activate_user(user_id)`  
Aktywuje konto użytkownika na podstawie kodu weryfikacyjnego.

**Endpoint:**  
`GET /users/{user_id}/activate`

**Parametry wejściowe:**  
| Typ parametru | Pole       | Typ      | Opis                                     | Wymagane? |
|---------------|------------|----------|------------------------------------------|-----------|
| **Path**      | `user_id`  | integer  | ID użytkownika do aktywacji.             | Tak       |
| **Query**     | `code`     | string   | Kod aktywacyjny z linku weryfikacyjnego. | Tak       |
| **Query**     | `email`    | string   | Email użytkownika powiązany z kontem.    | Tak       |

**Walidacja:**  
- Wymagane są parametry `code` i `email`.  
- Użytkownik musi istnieć w tabeli `user`.  
- Email musi zgadzać się z emailem przypisanym do `user_id`.  
- Kod musi być ważny i nieużyty (tabela `links` z typem `activate`).  

**Odpowiedzi:**  
- **200:** Konto aktywowane pomyślnie.  
  ```json
  {
    "message": "User activated successfully"
  }
  ```

  ---

### `deactivate_user(user_id)`  
Dezaktywuje konto użytkownika o określonym `user_id`.

**Endpoint:**  
`POST /users/{user_id}/deactivate`

**Parametry wejściowe:**  
- `user_id` (integer) – ID użytkownika (parametr ścieżki, wymagany).  
- Dane w formacie JSON w ciele żądania:  

| Pole        | Typ      | Opis                                     |
|-------------|----------|------------------------------------------|
| `password`  | string   | Hasło użytkownika (wymagane).            |

**Walidacja:**  
- Użytkownik musi być właścicielem konta (`user_id` musi pasować do tokena JWT).  
- Hasło musi być poprawne i zgodne z zapisanym w bazie.  

**Odpowiedzi:**  
- **200:** Konto dezaktywowane pomyślnie.  
  ```json
  {
    "message": "User deactivated"
  }
  ```
 --- 




## endpoints/diets.py
Funkcje odpowiedzialne za tworzenie, pobieranie listy diet oraz pobieranie szczegółowych informacji o diecie w aplikacji Flask.

---

### `create_diet()`
Tworzy nową dietę i zapisuje jej dane w bazie danych.

**Endpoint:**
`POST /diets`

**Dekoratory:**
- `@login_required` – Dostęp wymaga zalogowania użytkownika.

**Parametry wejściowe:**
Przyjmuje dane w formacie JSON w ciele żądania:
- `name` (string) – Nazwa diety (wymagane).
- `description` (string) – Opis diety (opcjonalne).

**Odpowiedzi:**
- **201:** Dieta została pomyślnie utworzona, zwraca id utworzonej diety.
- **400:** Brak wymaganych danych.
- **500:** Wewnętrzny błąd serwera.

---

### `get_diets()`
Zwraca listę diet z paginacją.

**Endpoint:**
`GET /diets`

**Parametry zapytania (query):**
- `limit` (integer) – Liczba diet na stronę (domyślnie: 10, minimalnie: 1).
- `page` (integer) – Numer strony (domyślnie: 1, minimalnie: 1).

**Odpowiedzi:**
- **200:** Lista diet wraz z informacjami o paginacji.
  ```json
  {
    "diets": [
      {
        "id": 1,
        "name": "Keto Diet",
        "description": "Low-carb, high-fat diet"
      },
      {
        "id": 2,
        "name": "Vegan Diet",
        "description": "Plant-based diet"
      }
    ],
    "total": 20,
    "pages": 2,
    "current_page": 1,
    "page_size": 10
  }
  ```
- **400:** Błędne parametry zapytania.
- **500:** Wewnętrzny błąd serwera.

---

### `get_diet(diet_id)`
Zwraca szczegółowe informacje o diecie na podstawie jej ID.

**Endpoint:**
`GET /diets/<diet_id>`

**Parametry ścieżki (path):**
- `diet_id` (integer) – ID diety (wymagane).

**Odpowiedzi:**
- **200:** Informacje o diecie.
  ```json
  {
    "id": 1,
    "name": "Keto Diet",
    "description": "Low-carb, high-fat diet"
  }
  ```
- **404:** Dieta o podanym ID nie została znaleziona.
- **500:** Wewnętrzny błąd serwera.


---



## endpoints/food_logs.py
Implementacja zarządzania logami posiłków. 


### `get_food_logs()`
Pobiera listę logów posiłków z bazy danych z obsługą paginacji.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry zapytania:**
- `limit` (domyślnie: 10) – Liczba logów do zwrócenia.
- `page` (domyślnie: 1) – Numer strony (paginacja).

**Działanie:**
1. Pobiera wartości `limit` i `page` z parametrów zapytania.
2. Sprawdza, czy oba parametry są liczbami dodatnimi.
3. Oblicza przesunięcie (`offset`) na podstawie `page` i `limit`.
4. Łączy się z bazą danych i wykonuje dwa zapytania:
   - Liczenie całkowitej liczby logów.
   - Pobranie logów z limitem i przesunięciem.
5. Zwraca JSON zawierający:
   - Listę logów.
   - Liczbę stron.
   - Obecny numer strony.
   - Rozmiar strony (`page_size`).

**Odpowiedzi:**
- **200 (przykład):**
```json
{
  "food_logs": [
    {
      "id": 1,
      "user_id": 123,
      "meal_history_id": 456,
      "portion": 1.5,
      "at": "2025-01-26T12:34:56Z"
    }
  ],
  "total": 100,
  "pages": 10,
  "current_page": 1,
  "page_size": 10
}
```


- **400**, gdy `limit` lub `page` są nieprawidłowe. 
- **500** w przypadku innych błędów.

---

### `get_food_log(food_log_id)`
Pobiera szczegóły pojedynczego logu posiłku według jego ID.


**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry ścieżki:**
- `food_log_id` (wymagane) – ID logu posiłku.

**Działanie:**
1. Łączy się z bazą danych i wykonuje zapytanie, aby pobrać log o podanym ID.
2. Jeśli log istnieje, zwraca jego dane w formacie JSON.
3. Jeśli log nie istnieje, zwraca kod 404 z informacją `Food log not found`.

**Odpowiedzi:**
- **200** (przykładowa)
```json
{
  "id": 1,
  "user_id": 123,
  "meal_history_id": 456,
  "portion": 1.5,
  "at": "2025-01-26T12:34:56Z"
}
```


- **404**, jeśli log nie zostanie znaleziony.
- **500** w przypadku innych błędów.

---


### `get_food_logs()`
Pobiera listę logów posiłków z bazy danych z obsługą paginacji.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry zapytania:**
- `limit` (domyślnie: 10) – Liczba logów do zwrócenia.
- `page` (domyślnie: 1) – Numer strony (paginacja).

**Logika:**
1. Pobiera wartości `limit` i `page` z parametrów zapytania.
2. Sprawdza, czy oba parametry są liczbami dodatnimi.
3. Oblicza przesunięcie (`offset`) na podstawie `page` i `limit`.
4. Łączy się z bazą danych i wykonuje dwa zapytania:
   - Liczenie całkowitej liczby logów.
   - Pobranie logów z limitem i przesunięciem.
5. Zwraca JSON zawierający:
   - Listę logów.
   - Liczbę stron.
   - Obecny numer strony.
   - Rozmiar strony (`page_size`).

**Odpowiedzi:**
- **200** (przykładowa)
```json
{
  "food_logs": [
    {
      "id": 1,
      "user_id": 123,
      "meal_history_id": 456,
      "portion": 1.5,
      "at": "2025-01-26T12:34:56Z"
    }
  ],
  "total": 100,
  "pages": 10,
  "current_page": 1,
  "page_size": 10
}
```

- **400**, gdy `limit` lub `page` są nieprawidłowe.
- **500** w przypadku innych błędów.

---

### `get_food_log(food_log_id)`
Pobiera szczegóły pojedynczego logu posiłku według jego ID.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry ścieżki:**
- `food_log_id` (wymagane) – ID logu posiłku.

**Logika:**
1. Łączy się z bazą danych i wykonuje zapytanie, aby pobrać log o podanym ID.
2. Jeśli log istnieje, zwraca jego dane w formacie JSON.
3. Jeśli log nie istnieje, zwraca kod 404 z informacją `Food log not found`.

**Odpowiedzi:**
- **200** (przykładowa)
```json
{
  "id": 1,
  "user_id": 123,
  "meal_history_id": 456,
  "portion": 1.5,
  "at": "2025-01-26T12:34:56Z"
}
```

- **404**, jeśli log nie zostanie znaleziony.
- **500** w przypadku innych błędów.

---

### `create_food_log`
Tworzy nowy log posiłku na podstawie danych przesłanych w żądaniu.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry żądania:**
- W ciele żądania (`body`) należy podać obiekt JSON z polami:
  - `meal_id` (wymagane) – ID posiłku.
  - `meal_version` (wymagane) – Wersja posiłku.
  - `portion` (wymagane) – Rozmiar porcji.
  - `at` (wymagane) – Czas w formacie `HH:MM:SS DD-MM-YYYY`.

**Logika:**
1. Pobiera dane z ciała żądania i sprawdza, czy wymagane pola są obecne.
2. Sprawdza autoryzację użytkownika (pobiera `user_id` z JWT).
3. Weryfikuje, czy posiłek (`meal_id` i `meal_version`) istnieje w tabeli `meal_history`.
4. Parsuje pole `at` do formatu datetime. Jeśli format jest nieprawidłowy, zwraca błąd.
5. Tworzy nowy wpis w tabeli `food_log` z podanymi danymi i przypisuje go do użytkownika.
6. Zwraca identyfikator nowo utworzonego logu.

**Odpowiedzi:**
- **201** (przykładowa)
```json
{
  "message": "Food log created",
  "food_log_id": 123
}
```

- **400**, jeśli brakuje wymaganych pól lub format daty jest nieprawidłowy.
- **404**, jeśli podany `meal_id` lub `meal_version` nie istnieje.
- **500**, jeśli wystąpi błąd bazy danych lub inny niespodziewany problem.

---

### `delete_food_log(food_log_id)`
Usuwa istniejący log posiłku na podstawie jego ID.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry ścieżki:**
- `food_log_id` (wymagane) – ID logu posiłku do usunięcia.

**Logika:**
1. Łączy się z bazą danych i sprawdza, czy log o podanym ID istnieje.
2. Jeśli log nie istnieje, zwraca błąd 404.
3. Sprawdza, czy użytkownik wykonujący żądanie ma uprawnienia do usunięcia logu (`verify_identity`).
4. Usuwa log z bazy danych i zatwierdza zmiany.
5. Zwraca komunikat o powodzeniu.

**Odpowiedzi:**
- **200**
```json
{
  "message": "Food log deleted"
}
```

- **404**, jeśli log o podanym ID nie istnieje.
- **403**, jeśli użytkownik nie ma uprawnień do usunięcia logu.
- **500**, jeśli wystąpi błąd bazy danych lub inny niespodziewany problem.


---

### `calculate_daily_nutrients(user_id, date)`
Oblicza dzienne spożycie kalorii i makroskładników dla użytkownika w danym dniu.

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry ścieżki:**
- `user_id` (wymagane) – ID użytkownika, dla którego obliczane są składniki odżywcze.
- `date` (wymagane) – Data w formacie `DD-MM-YYYY`.

**Parametry zapytania (opcjonalne):**
- `compareDetails` (boolean) – Określa, czy uwzględnić szczegóły porównania z celami użytkownika.

**Logika:**
1. Weryfikuje tożsamość użytkownika – tylko właściciel konta może obliczać składniki odżywcze.
2. Parsuje datę wejściową i definiuje zakres czasu (`start_date` i `end_date`) dla danego dnia.
3. Pobiera z bazy danych logi posiłków użytkownika dla określonego dnia.
4. Dla każdego logu posiłku:
   - Pobiera skład posiłku z tabeli `meal_history`.
   - Wylicza kalorie, białka, węglowodany i tłuszcze na podstawie składników (`ingredients`) i ich ilości.
5. Tworzy odpowiedź JSON zawierającą podsumowanie składników odżywczych.
6. Jeśli `compareDetails` jest ustawione na `true`, dodaje porównanie spożycia do celów użytkownika (`user_details`).

**Odpowiedzi:**
- **200** (przykładowa)
```json
{
  "date": "15-01-2025",
  "nutrients": {
    "total_kcal": 2000,
    "total_protein": 150,
    "total_carbs": 250,
    "total_fat": 50
  },
  "details": {
    "kcal_goal": 2200,
    "fat_goal": 70,
    "protein_goal": 160,
    "carb_goal": 300
  },
  "percentage": {
    "kcal_percentage": 90.91,
    "fat_percentage": 71.43,
    "protein_percentage": 93.75,
    "carbs_percentage": 83.33
  }
}
```

- **400**: Nieprawidłowy format daty.
- **403**: Brak uprawnień do przeglądania danych innego użytkownika.
- **500**: Niespodziewany błąd.

---

### `get_food_logs_by_date_for_user(user_id, date)`
Pobiera listę logów posiłków użytkownika dla określonego dnia.

**Ścieżka:**
Nie podano (do przypisania w konfiguracji Flaska).

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

**Parametry ścieżki:**
- `user_id` (wymagane) – ID użytkownika, którego logi mają zostać pobrane.
- `date` (wymagane) – Data w formacie `DD-MM-YYYY`.

**Logika:**
1. Weryfikuje tożsamość użytkownika – tylko właściciel konta może przeglądać swoje logi.
2. Parsuje datę i definiuje zakres (`start_date` i `end_date`) dla danego dnia.
3. Pobiera logi posiłków z tabeli `food_log` użytkownika dla określonego dnia.
4. Dla każdego logu:
   - Pobiera dane o składzie posiłku z tabeli `meal_history`.
   - Dodaje szczegóły posiłku do wyniku.
5. Zwraca listę logów w formacie JSON.

**Przykładowa odpowiedź (200):**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "meal_history_id": 456,
    "portion": 1.5,
    "at": "2025-01-15T12:30:00",
    "meal": "Grilled Chicken Salad"
  },
  {
    "id": 2,
    "user_id": 123,
    "meal_history_id": 457,
    "portion": 2,
    "at": "2025-01-15T19:00:00",
    "meal": "Spaghetti Bolognese"
  }
]
```

**Obsługa błędów:**
- Kod 400: Nieprawidłowy format daty.
- Kod 403: Brak uprawnień do przeglądania danych innego użytkownika.
- Kod 500: Niespodziewany błąd.

---


### `get_food_logs_for_user(user_id)`
Funkcja zwraca wszystkie logi posiłków dla określonego użytkownika. Wynik zawiera szczegóły posiłków, w tym ID logów, ich czas spożycia oraz skład.

---

**Dekorator:**
`@login_required` – wymaga autoryzacji JWT.

---

**Parametry**
- **Ścieżki:**
  - `user_id` *(integer, wymagane)* – ID użytkownika, którego logi mają zostać pobrane.

---

**Logika**
1. Weryfikuje, czy użytkownik próbuje pobrać swoje dane, przy użyciu funkcji `verify_identity`.
2. Łączy się z bazą danych i pobiera wszystkie logi z tabeli `food_log`, które są przypisane do podanego `user_id`.
3. Dla każdego logu pobiera szczegóły posiłku (`composition`) z tabeli `meal_history`.
4. Dodaje informacje o posiłku do wyników.
5. Zwraca listę logów w formacie JSON.

---

**Odpowiedzi:**
- **200** (przykładowa)
```json
[
  {
    "id": 1,
    "user_id": 123,
    "meal_history_id": 456,
    "portion": 2,
    "at": "2025-01-15T12:00:00",
    "meal": "Chicken Caesar Salad"
  },
  {
    "id": 2,
    "user_id": 123,
    "meal_history_id": 457,
    "portion": 1.5,
    "at": "2025-01-16T18:00:00",
    "meal": "Grilled Salmon with Veggies"
  }
]
```

- **403**, jeśli użytkownik próbuje uzyskać dostęp do logów innego użytkownika.
- **500**, w przypadku niespodziewanego błędu w trakcie działania funkcji.

---



## endpoints/food_schedule.py

---

### `get_food_schedules()`
Funkcja zwraca paginowaną listę wszystkich harmonogramów posiłków z tabeli `food_schedule`.

---

**Ścieżka:**  
`GET /food_schedules`

**Dekorator:**  
`@login_required` – wymaga autoryzacji JWT.

---

**Parametry:**
- **Query:**
  - `limit` *(integer, opcjonalny, domyślnie: 10)* – Liczba harmonogramów do zwrócenia na stronie.
  - `page` *(integer, opcjonalny, domyślnie: 1)* – Numer strony.

---

**Logika:**
1. Pobiera parametry paginacji z zapytania (limit i numer strony).
2. Sprawdza, czy podane wartości są dodatnie.
3. Oblicza offset na podstawie limitu i numeru strony.
4. Łączy się z bazą danych:
   - Pobiera łączną liczbę harmonogramów (`COUNT`).
   - Pobiera określoną liczbę rekordów (`LIMIT`) z tabeli `food_schedule`.
5. Zamyka połączenie z bazą.
6. Zwraca dane w formacie JSON:
   - Lista harmonogramów (`food_schedules`).
   - Łączna liczba rekordów (`total`).
   - Liczba stron (`pages`).
   - Obecna strona (`current_page`).
   - Rozmiar strony (`page_size`).

---

**Przykładowa odpowiedź (200):**
```json
{
  "food_schedules": [
    {
      "id": 1,
      "meal_history_id": 101,
      "at": "2025-01-15T12:00:00",
      "user_id": 123
    },
    {
      "id": 2,
      "meal_history_id": 102,
      "at": "2025-01-16T18:00:00",
      "user_id": 124
    }
  ],
  "total": 25,
  "pages": 3,
  "current_page": 1,
  "page_size": 10
}
```

- **400 – Bad Request:**  
  Jeśli `limit` lub `page` są mniejsze niż 1.
- **500 – Internal Server Error:**  
  W przypadku nieoczekiwanego błędu.

---

---

### `get_food_schedule(schedule_id)`
Funkcja zwraca szczegóły konkretnego harmonogramu posiłku na podstawie jego ID.

---

**Ścieżka:**  
`GET /food_schedules/<schedule_id>`

**Dekorator:**  
`@login_required` – wymaga autoryzacji JWT.

---

**Parametry:**
- **Ścieżki:**
  - `schedule_id` *(integer, wymagany)* – ID harmonogramu posiłku, który ma zostać zwrócony.

---

**Logika:**
1. Łączy się z bazą danych.
2. Wykonuje zapytanie do tabeli `food_schedule`, aby znaleźć rekord o podanym `schedule_id`.
3. Jeśli rekord istnieje, zwraca szczegóły harmonogramu w formacie JSON.
4. Jeśli rekord nie istnieje, zwraca komunikat o błędzie.
5. Zamknięcie połączenia z bazą danych po wykonaniu operacji.

---

**Odpowiedzi:**
- **200:** 
```json
{
  "id": 1,
  "meal_history_id": 101,
  "at": "2025-01-15T12:00:00",
  "user_id": 123
}
```

- **404**: Jeśli harmonogram o podanym `schedule_id` nie istnieje.
- **500**: W przypadku nieoczekiwanego błędu.

---

### `create_food_schedule()`
Tworzy nowy harmonogram posiłków.

- **Metoda HTTP**: POST  
- **Nagłówki**: `Authorization: Bearer <token>`  
**Parametry:**
  ```json
  {
    "meal_id": <integer>, 
    "meal_version": <integer>, 
    "at": "<HH:MM:SS DD-MM-YYYY>"
  }
  ```

- **Walidacja**:
  - `meal_id`, `meal_version`, `at` są wymagane.
  - `meal_id` i `meal_version` muszą istnieć w `meal_history`.
  - `at` musi być przyszłą datą.

- **Odpowiedzi**:
  - `201`: Harmonogram utworzony.  
    ```json
    {"message": "Food schedule created", "food_schedule_id": <integer>}
    ```
  - `400`: Nieprawidłowe dane wejściowe.  
  - `404`: Historia posiłków nie istnieje.  
  - `500`: Błąd serwera.

---

### `delete_food_schedule(schedule_id)`
Usuwa istniejący harmonogram.

- **Metoda HTTP**: DELETE  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**: `schedule_id` (integer)

- **Walidacja**:
  - Harmonogram musi istnieć w `food_schedule`.
  - Tylko twórca może go usunąć.

- **Odpowiedzi**:
  - `200`: Harmonogram usunięty.  
    ```json
    {"message": "Food schedule deleted"}
    ```
  - `404`: Harmonogram nie istnieje.  
  - `403`: Brak uprawnień.  
  - `500`: Błąd serwera.

---


### `get_food_schedule_for_user(user_id)`
Pobiera zaplanowane posiłki dla danego użytkownika.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `user_id` (integer) – ID użytkownika, którego harmonogramy mają zostać pobrane.

- **Odpowiedzi**:
  - `200`: Lista harmonogramów posiłków.  
    ```json
    [
      {
        "id": <integer>,
        "meal_history_id": <integer>,
        "at": "<date-time>",
        "user_id": <integer>,
        "meal": "<string>"
      }
    ]
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "An unexpected error occurred", "message": "<opis błędu>"}
    ```

---

### `get_food_schedule_for_user_by_date(user_id, date)`
Pobiera zaplanowane posiłki dla użytkownika w danym dniu.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `user_id` (integer) – ID użytkownika.  
  - `date` (string) – Data w formacie `DD-MM-YYYY`.

- **Walidacja**:
  - `date` musi być w formacie `DD-MM-YYYY`.

- **Odpowiedzi**:
  - `200`: Lista harmonogramów posiłków dla podanej daty.  
    ```json
    [
      {
        "id": <integer>,
        "meal_history_id": <integer>,
        "at": "<date-time>",
        "user_id": <integer>,
        "meal": "<string>"
      }
    ]
    ```
  - `400`: Nieprawidłowy format daty.  
    ```json
    {"error": "Invalid date format. Use 'DD-MM-YYYY'"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "An unexpected error occurred", "message": "<opis błędu>"}
    ```

---



## endpoints/ingredients.py  

### `get_ingredients()`
Pobiera listę składników z możliwością paginacji.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania**:
  - `limit` (integer, opcjonalny) – Liczba składników do zwrócenia (domyślnie: 10).  
  - `page` (integer, opcjonalny) – Numer strony (domyślnie: 1).  

- **Odpowiedzi**:
  - `200`: Lista składników z dodatkowymi metadanymi paginacji.  
    ```json
    {
      "ingredients": [
        {
          "id": <integer>,
          "product_name": "<string>",
          "generic_name": "<string>",
          "kcal_100g": <number>,
          "protein_100g": <number>,
          "carbs_100g": <number>,
          "fat_100g": <number>,
          "brand": "<string>",
          "barcode": "<string>",
          "image_url": "<string>",
          "labels_tags": "<string>",
          "product_quantity": <number>,
          "allergens": "<string>"
        }
      ],
      "total": <integer>,
      "pages": <integer>,
      "current_page": <integer>,
      "page_size": <integer>
    }
    ```
  - `400`: Nieprawidłowe parametry.  
    ```json
    {"error": "Limit and page must be positive integers"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `get_ingredient_by_id(ing_id)`
Pobiera szczegóły składnika na podstawie jego ID.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `ing_id` (integer) – ID składnika.  

- **Odpowiedzi**:
  - `200`: Obiekt składnika.  
    ```json
    {
      "id": <integer>,
      "product_name": "<string>",
      "generic_name": "<string>",
      "kcal_100g": <number>,
      "protein_100g": <number>,
      "carbs_100g": <number>,
      "fat_100g": <number>,
      "brand": "<string>",
      "barcode": "<string>",
      "image_url": "<string>",
      "labels_tags": "<string>",
      "product_quantity": <number>,
      "allergens": "<string>"
    }
    ```
  - `404`: Składnik nie został znaleziony.  
    ```json
    {"message": "Ingredient not found"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `search_ingredients()`  
Wykonuje wyszukiwanie pełnotekstowe składników na podstawie podanego zapytania.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania**:
  - `query` (string, opcjonalny) – Zapytanie wyszukiwania (domyślnie: pusty ciąg).  
  - `top` (integer, opcjonalny) – Liczba wyników do zwrócenia (domyślnie: 10).  

- **Odpowiedzi**:
  - `200`: Lista wyników wyszukiwania.  
    ```json
    [
      {
        "id": <integer>,
        "product_name": "<string>",
        "generic_name": "<string>",
        "kcal_100g": <number>,
        "protein_100g": <number>,
        "carbs_100g": <number>,
        "fat_100g": <number>,
        "brand": "<string>",
        "barcode": "<string>",
        "image_url": "<string>",
        "labels_tags": "<string>",
        "product_quantity": <number>,
        "allergens": "<string>"
      }
    ]
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---




## endpoints/meal_category.py  

### `get_meal_categories()`
Pobiera wszystkie dostępne kategorie posiłków.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`
- **Odpowiedzi**:
  - `200`: Lista kategorii posiłków.  
    ```json
    [
      {
        "id": <integer>,
        "name": "<string>",
        "description": "<string>"
      }
    ]
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `assign_category_to_meal(meal_id)`
Przypisuje kategorię do określonego posiłku.

- **Metoda HTTP**: POST  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer) – ID posiłku, do którego przypisywana jest kategoria.  
- **Treść żądania (body)**:
  - `category_id` (integer, wymagany) – ID kategorii, którą należy przypisać.  
    ```json
    {
      "category_id": <integer>
    }
    ```

- **Odpowiedzi**:
  - `200`: Kategoria została przypisana do posiłku.  
    ```json
    {"message": "Category assigned to meal"}
    ```
  - `400`: Nieprawidłowe dane wejściowe lub konflikt przypisania.  
    - Przykład błędu brakującego `category_id`:  
      ```json
      {"error": "category_id is required"}
      ```
    - Przykład błędu, gdy kategoria jest już przypisana:  
      ```json
      {"error": "Category is already assigned to this meal"}
      ```
  - `404`: Posiłek lub kategoria nie zostały znalezione.  
    - Przykład odpowiedzi dla brakującego posiłku:  
      ```json
      {"message": "Meal not found"}
      ```
    - Przykład odpowiedzi dla brakującej kategorii:  
      ```json
      {"message": "Category not found"}
      ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `remove_category_from_meal(meal_id)`  
Usuwa przypisaną kategorię z określonego posiłku.

- **Metoda HTTP**: DELETE  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, z którego ma zostać usunięta kategoria.  

- **Odpowiedzi**:
  - `200`: Kategoria została usunięta z posiłku.  
    ```json
    {"message": "Category removed from meal"}
    ```
  - `400`: Brak przypisanej kategorii lub błąd w żądaniu.  
    - Przykład odpowiedzi:  
      ```json
      {"error": "No category assigned to this meal"}
      ```
  - `404`: Posiłek nie został znaleziony.  
    ```json
    {"message": "Meal not found"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `update_category_of_meal(meal_id)`  
Aktualizuje kategorię przypisaną do określonego posiłku.

- **Metoda HTTP**: PUT  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, którego kategoria ma zostać zaktualizowana.  
- **Treść żądania (body)**:
  - `category_id` (integer, wymagany) – ID nowej kategorii.  
    ```json
    {
      "category_id": <integer>
    }
    ```

- **Odpowiedzi**:
  - `200`: Kategoria została zaktualizowana dla posiłku.  
    ```json
    {"message": "Category updated for meal"}
    ```
  - `400`: Błąd w żądaniu lub brak przypisanej kategorii.  
    - Przykład błędu brakującego `category_id`:  
      ```json
      {"error": "category_id is required"}
      ```
    - Przykład błędu braku przypisanej kategorii:  
      ```json
      {"error": "No category assigned to this meal"}
      ```
  - `404`: Posiłek lub nowa kategoria nie zostały znalezione.  
    - Przykład odpowiedzi dla brakującego posiłku:  
      ```json
      {"message": "Meal not found"}
      ```
    - Przykład odpowiedzi dla brakującej kategorii:  
      ```json
      {"message": "Category not found"}
      ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---




### `get_meal_ingredients(meal_id)`  
Pobiera składniki przypisane do konkretnego posiłku.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, którego składniki mają zostać pobrane.  

- **Odpowiedzi**:
  - `200`: Lista składników przypisanych do posiłku.  
    - Przykład odpowiedzi:  
      ```json
      [
        {
          "ingredient": {
            "id": 1,
            "product_name": "Sugar",
            "generic_name": "Sugar",
            "kcal_100g": 400,
            "protein_100g": 0,
            "carbs_100g": 100,
            "fat_100g": 0,
            "brand": "Brand X",
            "barcode": "123456789",
            "image_url": "https://example.com/image.jpg",
            "labels_tags": "vegan",
            "product_quantity": 500,
            "allergens": "None"
          },
          "details": {
            "meal_id": 1,
            "ingredient_id": 1,
            "unit": "grams",
            "quantity": 50
          }
        }
      ]
      ```
  - `404`: Posiłek nie został znaleziony.  
    ```json
    {"message": "Meal not found"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `replace_meal_ingredients(meal_id)`  
Zastępuje składniki przypisane do konkretnego posiłku nowym zestawem składników.

- **Metoda HTTP**: PUT  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, którego składniki mają zostać zaktualizowane.  
- **Treść żądania (body)**:
  - `ingredients` (array, wymagany) – Lista składników do przypisania.  
    - Przykład:  
      ```json
      {
        "ingredients": [
          {
            "ingredient_id": 1,
            "unit": "grams",
            "quantity": 100
          },
          {
            "ingredient_id": 2,
            "unit": "ml",
            "quantity": 50
          }
        ]
      }
      ```

- **Odpowiedzi**:
  - `200`: Składniki posiłku zostały pomyślnie zaktualizowane.  
    ```json
    {"message": "Meal ingredients updated successfully"}
    ```
  - `400`: Błąd w żądaniu.  
    - Przykład błędu brakującej listy składników:  
      ```json
      {"error": "Ingredients list is required"}
      ```
  - `404`: Posiłek nie został znaleziony.  
    ```json
    {"message": "Meal not found"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `add_meal_ingredient(meal_id)`  
Dodaje składnik do posiłku.

- **Metoda HTTP**: POST  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, do którego należy dodać składnik.  
- **Treść żądania (body)**:
  - Wymagane pola:  
    - `ingredient_id` (integer) – ID składnika do dodania.  
    - `unit` (string) – Jednostka składnika (np. "grams", "ml").  
    - `quantity` (number) – Ilość składnika.  
  - Przykład:  
    ```json
    {
      "ingredient_id": 1,
      "unit": "grams",
      "quantity": 100
    }
    ```

- **Odpowiedzi**:
  - `201`: Składnik został pomyślnie dodany.  
    ```json
    {"message": "Ingredient added successfully"}
    ```
  - `400`: Błąd w żądaniu.  
    - Brak wymaganych danych:  
      ```json
      {"error": "ingredient_id, unit, and quantity are required"}
      ```
    - Składnik już przypisany do posiłku:  
      ```json
      {"error": "This ingredient is already assigned to the meal"}
      ```
  - `404`: Posiłek nie został znaleziony.  
    ```json
    {"message": "Meal not found"}
    ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---

### `remove_meal_ingredient(meal_id, ingredient_id)`  
Usuwa składnik z posiłku.

- **Metoda HTTP**: DELETE  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku, z którego należy usunąć składnik.  
  - `ingredient_id` (integer, wymagany) – ID składnika do usunięcia.  

- **Odpowiedzi**:
  - `200`: Składnik został pomyślnie usunięty.  
    ```json
    {"message": "Ingredient removed successfully"}
    ```
  - `404`:  
    - Składnik nie został znaleziony w posiłku:  
      ```json
      {"error": "Ingredient not found in meal"}
      ```
    - Posiłek nie został znaleziony:  
      ```json
      {"message": "Meal not found"}
      ```
  - `500`: Błąd serwera.  
    ```json
    {"error": "Internal server error"}
    ```

---



## endpoints/meals.py

### `get_meals()`  
Pobiera listę posiłków.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (query)**:
  - `limit` (integer, opcjonalny) – Liczba posiłków do zwrócenia.  
    - Domyślnie: `10`.  
  - `page` (integer, opcjonalny) – Numer strony.  
    - Domyślnie: `1`.  

- **Odpowiedzi**:
  - `200`: Lista posiłków oraz informacje o paginacji.  
    - Przykład:  
      ```json
      {
        "meals": [
          {
            "id": 1,
            "name": "Breakfast",
            "description": "Morning meal",
            "creator_id": 2,
            "diet_id": 1,
            "category_id": 3,
            "version": 1,
            "last_update": "2025-01-25T12:00:00"
          }
        ],
        "total": 15,
        "pages": 2,
        "current_page": 1,
        "page_size": 10
      }
      ```
  - `400`: Nieprawidłowe dane w parametrach zapytania.  
    - Przykład:  
      ```json
      {"error": "Limit and page must be positive integers"}
      ```
  - `500`: Błąd serwera.  
    - Przykład:  
      ```json
      {"error": "Internal server error"}
      ```

---

### `get_meal(meal_id)`  
Pobiera posiłek na podstawie jego ID.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry ścieżki**:
  - `meal_id` (integer, wymagany) – ID posiłku do pobrania.  

- **Odpowiedzi**:
  - `200`: Szczegóły posiłku.  
    - Przykład:  
      ```json
      {
        "id": 1,
        "name": "Lunch",
        "description": "Midday meal",
        "creator_id": 2,
        "diet_id": 1,
        "category_id": 3,
        "version": 1,
        "last_update": "2025-01-25T12:00:00"
      }
      ```
  - `404`: Posiłek nie został znaleziony.  
    - Przykład:  
      ```json
      {"message": "Meal not found"}
      ```
  - `500`: Błąd serwera.  
    - Przykład:  
      ```json
      {"error": "Internal server error"}
      ```

---

### `search_meals()`  
Wyszukuje posiłki na podstawie zapytania i filtrów.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (query)**:
  - `query` (string, opcjonalny) – Zapytanie wyszukiwania.  
    - Domyślnie: `''`.  
  - `limit` (integer, opcjonalny) – Liczba posiłków do zwrócenia.  
    - Domyślnie: `10`.  
  - `page` (integer, opcjonalny) – Numer strony.  
    - Domyślnie: `1`.  
  - `allowMore` (boolean, opcjonalny) – Czy umożliwić większą liczbę wyników.  
    - Domyślnie: `False`.  
  - `user_id` (integer, opcjonalny) – ID użytkownika (jeśli nie podane, używany jest token JWT do pobrania ID).  

- **Odpowiedzi**:
  - `200`: Lista posiłków pasujących do zapytania oraz informacje o paginacji.  
    - Przykład:  
      ```json
      {
        "meals": [
          {
            "id": 1,
            "name": "Vegetarian Salad",
            "description": "Healthy salad with veggies",
            "creator_id": 2,
            "diet_id": 1,
            "category_id": 3,
            "version": 1,
            "last_update": "2025-01-25T12:00:00"
          }
        ],
        "total": 5,
        "pages": 1,
        "current_page": 1,
        "page_size": 10
      }
      ```
  - `400`: Nieprawidłowe dane w parametrach zapytania.  
    - Przykład:  
      ```json
      {"error": "Limit and page must be positive integers"}
      ```
  - `500`: Błąd serwera.  
    - Przykład:  
      ```json
      {"error": "Internal server error"}
      ```

---


### `create_meal()`  
Tworzy nowy posiłek w systemie.

- **Metoda HTTP**: POST  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (body)**:
  - `name` (string, wymagany) – Nazwa posiłku.
  - `description` (string, opcjonalny) – Opis posiłku.
  - `diet_id` (integer, opcjonalny) – ID diety, do której należy posiłek.
  - `category_id` (integer, opcjonalny) – ID kategorii, do której należy posiłek.
  - `ingredients` (array, opcjonalny) – Lista składników, które zawiera posiłek. Każdy składnik jest obiektem z polami:
    - `ingredient_id` (integer) – ID składnika.
    - `unit` (string) – Jednostka miary.
    - `quantity` (number) – Ilość składnika.

- **Odpowiedzi**:
  - `201`: Posiłek został pomyślnie utworzony.
    - Przykład:  
      ```json
      {
        "message": "Meal created",
        "meal_id": 1
      }
      ```
  - `400`: Złe dane wejściowe (np. brak nazwy).
    - Przykład:  
      ```json
      {"error": "Name is required"}
      ```
  - `404`: Kategoria lub dieta nie została znaleziona.
    - Przykład:  
      ```json
      {"error": "Category not found"}
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error",
        "message": "Detailed error message"
      }
      ```

---

### `update_meal()`  
Aktualizuje informacje o posiłku na podstawie ID posiłku.

- **Metoda HTTP**: PUT  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (path)**:
  - `meal_id` (integer, wymagany) – ID posiłku, który ma zostać zaktualizowany.
- **Parametry zapytania (body)**:
  - `name` (string, opcjonalny) – Nazwa posiłku.
  - `description` (string, opcjonalny) – Opis posiłku.
  - `diet_id` (integer, opcjonalny) – ID diety, do której należy posiłek.
  - `category_id` (integer, opcjonalny) – ID kategorii, do której należy posiłek.

- **Odpowiedzi**:
  - `200`: Posiłek został pomyślnie zaktualizowany.
    - Przykład:  
      ```json
      {
        "message": "Meal updated",
        "meal_id": 1
      }
      ```
  - `400`: Błędy związane z parametrami zapytania (np. próba aktualizacji składników przez nieodpowiedni endpoint).
    - Przykład:  
      ```json
      {"error": "To update ingredients, use the /meals/<meal_id>/ingredients endpoint"}
      ```
  - `404`: Posiłek nie został znaleziony.
    - Przykład:  
      ```json
      {"message": "Meal not found"}
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error"
      }
      ```

---


### `delete_meal()`  
Usuwa posiłek na podstawie ID posiłku.

- **Metoda HTTP**: DELETE  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (path)**:
  - `meal_id` (integer, wymagany) – ID posiłku, który ma zostać usunięty.

- **Odpowiedzi**:
  - `200`: Posiłek został pomyślnie usunięty.
    - Przykład:  
      ```json
      {
        "message": "Meal deleted"
      }
      ```
  - `404`: Posiłek o podanym ID nie został znaleziony.
    - Przykład:  
      ```json
      {"message": "Meal not found"}
      ```
  - `403`: Użytkownik nie jest upoważniony do usunięcia posiłku (np. próba usunięcia posiłku, który nie został stworzony przez tego użytkownika).
    - Przykład:  
      ```json
      {
        "error": "Unauthorized",
        "message": "You can only delete meals you created"
      }
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error"
      }
      ```

---

### `get_meal_versions()`  
Pobiera wersje posiłku na podstawie jego ID.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (path)**:
  - `meal_id` (integer, wymagany) – ID posiłku, dla którego mają zostać zwrócone wersje.

- **Odpowiedzi**:
  - `200`: Zwraca listę wersji posiłku, w tym dane takie jak ID posiłku, numer wersji oraz skład posiłku.
    - Przykład:  
      ```json
      {
        "meal_versions": [
          {
            "meal_id": 1,
            "meal_version": 1,
            "composition": "{\"name\": \"Meal 1\", \"description\": \"A description\"}"
          },
          {
            "meal_id": 1,
            "meal_version": 2,
            "composition": "{\"name\": \"Meal 1\", \"description\": \"Updated description\"}"
          }
        ]
      }
      ```
  - `404`: Posiłek o podanym ID nie został znaleziony w historii.
    - Przykład:  
      ```json
      {"message": "Meal not found"}
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error"
      }
      ```

---

### `get_meal_nutrients()`  
Pobiera dane o wartościach odżywczych posiłku na podstawie jego ID.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (path)**:
  - `meal_id` (integer, wymagany) – ID posiłku, dla którego mają zostać zwrócone wartości odżywcze.

- **Odpowiedzi**:
  - `200`: Zwraca dane o wartościach odżywczych posiłku, w tym sumę kalorii, białka, węglowodanów i tłuszczów, a także wartości te przeliczone na 100g posiłku.
    - Przykład:  
      ```json
      {
        "nutrients": {
          "total_calories": 450,
          "total_protein": 20,
          "total_carbs": 55,
          "total_fat": 15
        },
        "nutrients_per_100g": {
          "calories": 250,
          "protein": 11,
          "carbs": 15,
          "fat": 8
        }
      }
      ```
  - `404`: Posiłek o podanym ID nie został znaleziony.
    - Przykład:  
      ```json
      {"message": "Meal not found"}
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error"
      }
      ```



## endpoints/shopping_list.py

---
### `generate_shopping_list()`  
Generuje listę zakupów na podstawie zaplanowanych posiłków dla użytkownika na określoną liczbę dni.

- **Metoda HTTP**: GET  
- **Nagłówki**: `Authorization: Bearer <token>`  
- **Parametry zapytania (path)**:
  - `user_id` (integer, wymagany) – ID użytkownika, dla którego ma zostać wygenerowana lista zakupów.
- **Parametry zapytania (query)**:
  - `days` (integer, opcjonalny, domyślnie 7) – liczba dni, na które ma zostać wygenerowana lista zakupów.
  
- **Odpowiedzi**:
  - `200`: Zwraca wygenerowaną listę zakupów, w tym zaplanowane posiłki z odpowiednimi składnikami oraz zbiorczą listę produktów.
    - Przykład:  
      ```json
      {
        "meals": [
          {
            "meal": "Spaghetti",
            "ingredients": [
              {
                "ingredient": {
                  "id": 1,
                  "product_name": "Pasta",
                  "generic_name": "Pasta",
                  "kcal_100g": 200,
                  "protein_100g": 7,
                  "carbs_100g": 30,
                  "fat_100g": 1,
                  "brand": "Brand A",
                  "barcode": "123456",
                  "image_url": "http://example.com/image.jpg",
                  "labels_tags": "vegan",
                  "product_quantity": 500,
                  "allergens": "gluten"
                },
                "quantity": 100,
                "unit": "g"
              }
            ]
          }
        ],
        "ingredients_summary": [
          {
            "ingredient": {
              "id": 1,
              "product_name": "Pasta",
              "generic_name": "Pasta",
              "kcal_100g": 200,
              "protein_100g": 7,
              "carbs_100g": 30,
              "fat_100g": 1,
              "brand": "Brand A",
              "barcode": "123456",
              "image_url": "http://example.com/image.jpg",
              "labels_tags": "vegan",
              "product_quantity": 500,
              "allergens": "gluten"
            },
            "total_quantity": 100,
            "unit": "g"
          }
        ]
      }
      ```
  - `400`: Błąd zapytania (np. niepoprawna liczba dni).
    - Przykład:  
      ```json
      {"error": "Days must be a positive integer"}
      ```
  - `500`: Błąd serwera.
    - Przykład:  
      ```json
      {
        "error": "Internal server error"
      }
      ```

