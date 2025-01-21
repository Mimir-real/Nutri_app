# Aplikacja do zarządzania dietami

Aplikacja umożliwia zarządzanie dietami, posiłkami oraz logowaniem żywności. Funkcjonalności obejmują rejestrację użytkowników, przypisywanie diet, tworzenie posiłków, składników oraz śledzenie spożycia.

## Spis treści

1. [Wymagania](#wymagania)
2. [Instalacja](#instalacja)
3. [Konfiguracja](#konfiguracja)
4. [Uruchomienie](#uruchomienie)
5. [Struktura projektu](#struktura-projektu)
6. [Dodawanie danych do bazy](#dodawanie-danych-do-bazy)
7. [Wykorzystane technologie](#wykorzystane-technologie)

---

## Wymagania

Aby uruchomić projekt, wymagane są:

- **Python 3.7+**
- **pip** (Python Package Installer)
- **Virtualenv** (zalecane do izolacji środowiska)
- **PostgreSQL** (instalacja lokalna lub dostęp do zdalnej bazy)

---

## Instalacja

1. **Sklonuj repozytorium:**

   ```bash
   git clone https://github.com/Mimir-real/bazany_danych_proj.git
   cd bazany_danych_proj
   ```

2. **Utwórz i aktywuj wirtualne środowisko:**

   **Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Zainstaluj PostgreSQL:**
   Pobierz i zainstaluj PostgreSQL z oficjalnej strony lub skorzystaj z usługi chmurowej.

5. **Skonfiguruj bazę danych PostgreSQL:**

   Zaloguj się do PostgreSQL i utwórz nową bazę danych:
   ```sql
   CREATE DATABASE bazaDanych;
   ```

6. **Utwórz plik `.env` i skonfiguruj połączenie:**
   
   ```plaintext
   DB_NAME=bazaDanych
   DB_USER=postgres
   DB_PASSWORD=1234
   DB_HOST=localhost
   DB_PORT=5432
   ```
   
---

## Uruchomienie

1. **Inicjalizacja bazy danych:**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

2. **Zaimportowanie danych:**
   
   ```bash
   python3 app.py dbinit
   ```

3. **Uruchomienie aplikacji:**
   
   ```bash
   flask run
   ```
   
   Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:5000`

---

## Struktura projektu

```
diet-app/
│
├── app.py                # Główny plik aplikacji Flask
├── db_config.py          # Konfiguracja bazy danych
├── seeds.py              # Inicjalizacja danych w bazie
├── .env                  # Plik konfiguracyjny
├── requirements.txt      # Plik z zależnościami
└── README.md             # Dokumentacja projektu
```

---

## Dodawanie danych do bazy

Po uruchomieniu aplikacji dane początkowe zostaną załadowane automatycznie, jeśli wywołasz funkcję `setup_database()` z pliku `seeds.py`.

Możesz ręcznie załadować dane w terminalu:

```python
from app import setup_database
setup_database()
```

---

## Wykorzystane technologie

- **Flask** - framework webowy do budowy aplikacji w Pythonie
- **PostgreSQL** - baza danych
- **python-dotenv** - obsługa zmiennych środowiskowych

---

