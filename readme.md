# Aplikacja do zarządzania dietami

Aplikacja umożliwia zarządzanie dietami, posiłkami oraz logowaniem żywności. Funkcjonalności obejmują rejestrację użytkowników, przypisywanie diet, tworzenie posiłków, składników oraz śledzenie spożycia.

## Spis treści

1. [Wymagania](#wymagania)
2. [Uruchomienie przez Docker](#uruchomienie-poprzez-docker)
3. [Struktura projektu](#struktura-projektu)
4. [Wykorzystane technologie](#wykorzystane-technologie)

---

## Wymagania

- **Docker** (konteneryzacja, uruchomienie)

---

## Uruchomienie poprzez Docker

Aby uruchomić aplikację w kontenerze Docker, wykonaj następujące kroki:

1. **Zainstaluj Dockera**  

   Jeśli nie masz zainstalowanego Dockera, pobierz i zainstaluj go z [oficjalnej strony](https://www.docker.com/get-started).

2. **Sklonuj repozytorium:**
   
   ```bash
   git clone https://github.com/Mimir-real/bazany_danych_proj.git
   cd bazany_danych_proj
   ```
   _(Zwróć uwagę na poprawny link do repozytorium)_

3. **Dostosuj docker-compose.yml (opcjonalne)**

   Jeśli chcesz dostosować konfigurację Docker Compose, możesz edytować plik `docker-compose.yml`. 
   Na przykład, możesz zmienić porty, zmienne środowiskowe lub inne ustawienia usług.

4. **Uruchomienie aplikacji**  

   W terminalu wykonaj następujące polecenia:

   ```bash
   docker-compose up
   ```

5. **Dodatkowa konfiguracja (ważne)**

  Podczas uruchamiania komendy z punktu 4. może wystąpić błąd związany ze skryptem inicjalizującym początkowy stan bazy danych.

  Przykładowy błąd:
  ```bash
  (output omitted)
db-1   | 
db-1   | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/backup.dump
db-1   | 
db-1   | /usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/import_backup.sh
db-1   | /usr/local/bin/docker-entrypoint.sh: line 174: /docker-entrypoint-initdb.d/import_backup.sh: cannot execute: required file not found
db-1 exited with code 127
Gracefully stopping... (press Ctrl+C again to force)
dependency failed to start: container bazany_danych_proj-db-1 exited (127)
  ```
  
W takim przypadku należy użyć komendy z punktu 4 jeszcze raz (uruchomienie aplikacji) oraz wykonać manualny import stanu początkowego bazy danych poprzez użycie komendy (musisz być w katalogu projektu, aby ścieżka do `backup.dump` była poprawna):

  ```bash
  docker exec -i bazany_danych_proj-db-1 pg_restore -U postgres -v -d bazaDanych < db\backup.dump
  ```
  _(`bazany_danych_proj-db-1` to kontener zawierający bazę pod aplikację, nazwa ta może się różnić. Upewnij się jak nazywa się twój kontener używając komendy `docker ps -a`)_

6. **Sprawdzenie działania**  

   **UWAGA!** Za pierwszym razem, gdy wykonuje się inicjalizacja stanu początkowego bazy aplikacja do poprawnego działania może wymagać troche więcej czasu.

   Po uruchomieniu aplikacja powinna być dostępna pod adresem:

   ```bash
   http://127.0.0.1:5000/
   ```

   Dokumentacja będzie dostępna pod adresem

   ```bash
   http://127.0.0.1:5000/apidocs/
   ```

7. **Zatrzymanie aplikacji**  

   Aby zatrzymać i usunąć kontenery, wykonaj:

   ```bash
   docker-compose down -v
   ```

   Aby zatrzymać kontenery i móc skorzystać z nich później, wykonaj:

   ```bash
   docker-compose down
   ```

---

## Struktura projektu

```
diet-app/
├── db/                   # Zrzut bazy danych i skrypt inicjujący stan początkowy
├── app.py                # Główny plik aplikacji Flask
├── endpoints/            # Endpointy aplikacji
├── db_config.py          # Konfiguracja bazy danych
├── requirements.txt      # Plik z zależnościami
└── README.md             # Dokumentacja projektu
```

---

## Wykorzystane technologie

- **Flask** - framework webowy do budowy aplikacji w Pythonie
- **PostgreSQL** - baza danych
- **python-dotenv** - obsługa zmiennych środowiskowych
- **Docker** - konteneryzacja aplikacji

---

