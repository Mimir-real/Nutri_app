# Użycie lekkiego obrazu Pythona
FROM python:3.11-alpine

# Zainstalowanie wymaganych pakietów systemowych
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Skopiowanie plików aplikacji
COPY . .

# Instalacja zależności z pliku requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ustawienie zmiennych środowiskowych Flaska
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Wystawienie portu 5000
EXPOSE 5000

# Polecenie startowe (uruchomienie aplikacji Flask)
CMD ["flask", "run"]
