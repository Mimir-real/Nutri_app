# Aplikacja do zarządzania dietami

Aplikacja umożliwia zarządzanie dietami, posiłkami oraz logowaniem żywności. Funkcjonalności obejmują rejestrację użytkowników, przypisywanie diet, tworzenie posiłków, składników oraz śledzenie spożycia.

## Spis treści

1. [Wymagania](#wymagania)
2. [Uruchomienie przez Docker](#uruchomienie-poprzez-docker)
3. [Struktura projektu](#struktura-projektu)
4. [Dodawanie danych do bazy](#dodawanie-danych-do-bazy)
5. [Wykorzystane technologie](#wykorzystane-technologie)

---

## Wymagania

Aby uruchomić projekt, wymagane są:

- **Python 3.7+**
- **pip** (Python Package Installer)
- **Virtualenv** (zalecane do izolacji środowiska)
- **PostgreSQL** (instalacja lokalna lub dostęp do zdalnej bazy)

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

3. **Uruchomienie aplikacji**  
   W terminalu wykonaj następujące polecenia:

   ```bash
   docker-compose up
   ```

   Aplikacja zostanie uruchomiona w tle.

4. **Sprawdzenie działania**  
   Po uruchomieniu dokumentacja aplikacja powinna być dostępna pod adresem:

   ```bash
   http://127.0.0.1:5000/apidocs
   ```

5. **Zatrzymanie aplikacji**  
   Aby zatrzymać i usunąć kontenery, wykonaj:

   ```bash
   docker-compose down
   ```

--

## Struktura projektu

```
diet-app/
├── app.py                # Główny plik aplikacji Flask
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

