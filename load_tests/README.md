# Appartners API Load Testing

This directory contains load testing scripts for the Appartners backend API using Locust.

## Setup

1. Install Locust:
```bash
pip install locust
```

2. Add it to your requirements.txt:
```bash
echo "locust==2.15.1" >> ../requirements.txt
```

## Running the Load Tests

From the project root directory, run:

```bash
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

Replace `http://localhost:8000` with your API server URL.

## Web Interface

Once started, access the Locust web interface at:
- http://localhost:8089

From there, you can:
1. Set the number of users to simulate
2. Set the spawn rate (users per second)
3. Start the test and monitor results in real-time

## Test Scenarios

The load test simulates users performing various actions:

- **Authentication**: Login, token refresh
- **User Profile**: Viewing and updating user preferences
- **Apartments**: Browsing recommendations, viewing details, liking/unliking apartments
- **Questionnaire**: Getting questions and submitting responses

## Running Specific Test Groups

You can run specific test groups using tags:

```bash
locust -f load_tests/locustfile.py --host=http://localhost:8000 --tags auth,user
```

Available tags:
- `auth`: Authentication operations
- `user`: User profile operations
- `apartment`: Apartment-related operations
- `questionnaire`: Questionnaire operations
