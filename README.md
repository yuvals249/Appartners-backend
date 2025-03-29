# Appartners-backend

python3/python -m venv path/to/venv

source path/to/venv/bin/activate

pip install -r requirements.txt

python3 manage.py runserver

docker run -it -e POSTGRES_PASSWORD=YOUR_PASSWORD -e POSTGRES_USER=YOUR_USER -e POSTGRES_DB=YOUR_DB -p DOCKER_PORT:YOUR_PORT postgres:latest