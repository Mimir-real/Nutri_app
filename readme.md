Aplikacja do zarządzania dietami, posiłkami i logowaniem żywności. Umożliwia rejestrację użytkowników, przypisywanie diet, tworzenie posiłków, składników oraz śledzenie spożycia posiłków.
Spis treści

   1. Wymagania
   2. Instalacja
   3. Konfiguracja
   4. Uruchomienie
   5. Struktura projektu
   6. Dodawanie danych do bazy
   7. Wykorzystane technologie


# Wymagania

Aby uruchomić projekt, musisz mieć zainstalowane poniższe narzędzia:

    Python 3.7+
    pip (Python Package Installer)
    Virtualenv (zalecane do izolacji środowiska)
    PostgreSQL (instalacja na maszynie lokalnej lub dostęp do zdalnej bazy PostgreSQL)

# Instalacja

    Sklonuj repozytorium:

git clone https://github.com/Mimir-real/bazany_danych_proj.git
cd bazany_danych_proj

## Utwórz i aktywuj wirtualne środowisko:

### Na systemie Windows:

python -m venv venv
.\venv\Scripts\activate

### Na systemie macOS/Linux:

python3 -m venv venv
source venv/bin/activate

## Zainstaluj zależności:

W katalogu głównym repozytorium uruchom:

pip install -r requirements.txt

To polecenie zainstaluje wszystkie wymagane pakiety, takie jak Flask, Flask-SQLAlchemy, Flask-WTF, python-dotenv i inne zależności.

Zainstaluj PostgreSQL:

Jeśli jeszcze tego nie zrobiłeś, zainstaluj PostgreSQL na swoim komputerze lub skorzystaj z zewnętrznej usługi bazy danych PostgreSQL. Możesz pobrać PostgreSQL tutaj.

Skonfiguruj bazę danych PostgreSQL:

    Utwórz bazę danych w PostgreSQL:

    Zaloguj się do PostgreSQL i utwórz nową bazę danych, na przykład:

    CREATE DATABASE bazaDanych;

Skonfiguruj połączenie z bazą danych:

Utwórz plik .env w katalogu głównym projektu i ustaw odpowiednie zmienne środowiskowe, takie jak dane dostępowe do bazy danych. Przykład pliku .env:
```
    DATABASE_URL=postgresql://postgres:postgres@adresIP:PORT/Nazwa

    SECRET_KEY=your-secret-key  # Ustaw unikalny klucz do sesji i formularzy
```
       DATABASE_URL: Wartość ta powinna zawierać dane do Twojej bazy danych PostgreSQL, w tym nazwę użytkownika, hasło, host, port i nazwę bazy danych.
        SECRET_KEY: Ustaw unikalny sekret, który będzie używany do sesji i formularzy w aplikacji Flask.

    Możesz utworzyć .env ręcznie lub przy pomocy edytora tekstu.

Konfiguracja

    Załaduj zmienne środowiskowe:

    Używamy biblioteki python-dotenv, która automatycznie ładuje dane z pliku .env do aplikacji. Upewnij się, że w Twoim projekcie jest zainstalowana ta biblioteka.

    W kodzie aplikacji, w pliku app.py, dodaj następujący kod do załadowania zmiennych z pliku .env:

from dotenv import load_dotenv
import os

load_dotenv()  # Ładuje zmienne z pliku .env

Połączenie z bazą danych:

W pliku config.py, zmień sposób łączenia się z bazą danych, aby korzystał z wartości zawartej w zmiennej środowiskowej DATABASE_URL. Możesz to zrobić, używając os.getenv():

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Pobiera URL bazy danych z .env
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # Jeśli SECRET_KEY nie jest ustawiony, używa wartości domyślnej

Zainstaluj bibliotekę python-dotenv:

Jeśli jeszcze tego nie zrobiłeś, zainstaluj bibliotekę python-dotenv:

    pip install python-dotenv

Uruchomienie

    Inicjalizacja bazy danych:

    Zanim uruchomisz aplikację, musisz upewnić się, że baza danych jest poprawnie skonfigurowana i tabele są utworzone. Możesz to zrobić uruchamiając migracje w Flasku:
```
flask db init        # Tworzy folder migrations
flask db migrate     # Generuje pliki migracji
flask db upgrade     # Aplikuje migracje do bazy danych
```
Jeśli używasz PostgreSQL, upewnij się, że masz dostęp do bazy danych, którą utworzyłeś wcześniej.

# Uruchom aplikację:

Po skonfigurowaniu bazy danych uruchom aplikację:

    flask run

    Domyślnie aplikacja będzie dostępna pod adresem: http://127.0.0.1:5000.

Struktura projektu
```
diet-app/
│
├── app.py                # Główny plik aplikacji Flask
├── config.py             # Konfiguracja aplikacji
├── models.py             # Modele SQLAlchemy
├── seeds.py              # Inicjalizacja danych w bazie danych
├── migrations/           # Folder z migracjami bazy danych
├── .env                  # Plik konfiguracyjny z danymi środowiskowymi
├── requirements.txt      # Plik z zależnościami
└── README.md             # Ten plik
```
# Dodawanie danych do bazy

Po uruchomieniu aplikacji, dane początkowe zostaną załadowane do bazy danych automatycznie, jeśli uruchomisz funkcję setup_database() (zdefiniowaną w seeds.py).

Możesz również ręcznie uruchomić tę funkcję w terminalu, aby załadować dane:
`
from app import setup_database
setup_database()
`
# Wykorzystane technologie

    Flask: Framework webowy do budowy aplikacji w Pythonie.
    Flask-SQLAlchemy: Rozszerzenie do integracji Flask z SQLAlchemy (ORM).
    Flask-WTF: Formularze webowe oparte na Flasku.
    Flask-Migrate: Rozszerzenie do zarządzania migracjami bazy danych.
    PostgreSQL: Baza danych SQL.
    python-dotenv: Biblioteka do ładowania zmiennych środowiskowych z pliku .env.

