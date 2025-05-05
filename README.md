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

### Redis (Required for WebSockets)
The application uses Redis for WebSocket support. You need to have Redis installed and running for real-time chat functionality to work properly.

#### Installing Redis

##### macOS
Using Homebrew:
```bash
brew install redis
```

##### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install redis-server
```

##### Windows
Redis is not officially supported on Windows, but you can use:
1. WSL (Windows Subsystem for Linux) to run Redis
2. Docker to run Redis in a container
3. Redis for Windows from Microsoft: https://github.com/microsoftarchive/redis/releases

#### Starting Redis

##### macOS
```bash
brew services start redis
```

##### Linux
```bash
sudo systemctl start redis-server
```

##### Docker (all platforms)
```bash
docker run -p 6379:6379 -d redis
```

#### Testing Redis Connection
You can test if Redis is running with:

```bash
redis-cli ping
```

If Redis is running, it should respond with `PONG`.

### Run
python3/python manage.py runserver
