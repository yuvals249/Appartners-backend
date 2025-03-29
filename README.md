# Appartners-backend

python3/python -m venv path/to/venv

source path/to/venv/bin/activate

pip install -r requirements.txt

python3 manage.py runserver

docker run -it -e POSTGRES_PASSWORD=DB_PASSWORD -e POSTGRES_USER=DB_USER -e POSTGRES_DB=DB_NAME -p DOCKER_PORT:DB_PORT postgres:latest