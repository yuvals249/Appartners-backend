# Appartners-backend

## Setup

### Virtual Environment
python3/python -m venv path/to/venv
source path/to/venv/bin/activate

### Dependencies
pip install -r requirements.txt

### Database
docker run -it -e POSTGRES_PASSWORD=DB_PASSWORD -e POSTGRES_USER=DB_USER -e POSTGRES_DB=DB_NAME -p DOCKER_PORT:DB_PORT postgres:latest

## Run

### Migrate
python3/python manage.py migrate

### Run
python3/python manage.py runserver

