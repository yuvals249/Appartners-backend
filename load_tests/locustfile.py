import json
import random
import time
import logging
from locust import HttpUser, task, between, tag, events
from locust.exception import StopUser

# Setup and teardown hooks
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    logging.info("Initializing Locust environment for Appartners API testing")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logging.info("Load test is starting")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("Load test is stopping")

class AppartnerUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks
    token = None
    user_id = None
    apartment_ids = []
    test_email = None
    test_password = "testpassword123"
    failed_requests = 0
    max_failed_requests = 5
    
    def on_start(self):
        """Log in at the start of the test"""
        try:
            self.test_email = f"test_user_{int(time.time())}_{random.randint(1000, 9999)}@example.com"
            self.login()
            self.get_apartments()
        except Exception as e:
            logging.error(f"Error during user startup: {str(e)}")
            raise StopUser()
            
    def on_stop(self):
        """Clean up after test"""
        if self.token:
            try:
                self.client.post(
                    "/api/v1/authenticate/logout/",
                    name="/api/v1/authenticate/logout"
                )
                logging.info(f"User {self.user_id} logged out successfully")
            except Exception as e:
                logging.error(f"Error during logout: {str(e)}")
                
    def request_success_handler(self, request_type, name, response_time, response_length, **kwargs):
        """Reset failed request counter on success"""
        self.failed_requests = 0
        
    def request_failure_handler(self, request_type, name, response_time, exception, **kwargs):
        """Track failed requests and stop user if too many consecutive failures"""
        self.failed_requests += 1
        logging.warning(f"Request failed: {name}, exception: {str(exception)}")
        
        if self.failed_requests >= self.max_failed_requests:
            logging.error(f"Too many consecutive failures ({self.failed_requests}), stopping user")
            raise StopUser()
    
    def login(self):
        """Authenticate and get token"""
        credentials = {
            "email": f"test_user_{int(time.time())}@example.com",
            "password": "testpassword123"
        }
        
        # Try to login with test user
        response = self.client.post(
            "/api/v1/authenticate/login/",
            json=credentials,
            name="/api/v1/authenticate/login"
        )
        
        # If login fails, register a new user
        if response.status_code != 200:
            register_data = {
                "email": credentials["email"],
                "password": credentials["password"],
                "first_name": "Test",
                "last_name": "User",
                "phone_number": f"+1{random.randint(1000000000, 9999999999)}"
            }
            
            self.client.post(
                "/api/v1/authenticate/register/",
                json=register_data,
                name="/api/v1/authenticate/register"
            )
            
            # Try login again
            response = self.client.post(
                "/api/v1/authenticate/login/",
                json=credentials,
                name="/api/v1/authenticate/login"
            )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result.get("token", "")
            self.user_id = result.get("user_id", "")
            # Set authorization header for future requests
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def get_apartments(self):
        """Get available apartments to use in other tests"""
        response = self.client.get(
            "/api/v1/apartments/recommendations/",
            name="/api/v1/apartments/recommendations"
        )
        
        if response.status_code == 200:
            apartments = response.json()
            if isinstance(apartments, list) and len(apartments) > 0:
                # Store apartment IDs for later use
                self.apartment_ids = [apt.get("id") for apt in apartments if apt.get("id")]
    
    # Authentication Tasks
    
    @tag("auth")
    @task(1)
    def refresh_token(self):
        """Refresh authentication token"""
        if self.token:
            self.client.post(
                "/api/v1/authenticate/token/refresh/",
                json={"token": self.token},
                name="/api/v1/authenticate/token/refresh"
            )
    
    # User Profile Tasks
    
    @tag("user")
    @task(3)
    def get_current_user(self):
        """Get current user profile"""
        self.client.get(
            "/api/v1/users/me/",
            name="/api/v1/users/me"
        )
    
    @tag("user")
    @task(1)
    def update_user_preferences(self):
        """Update user preferences"""
        preferences = {
            "min_price": random.randint(500, 1000),
            "max_price": random.randint(1500, 3000),
            "min_rooms": random.randint(1, 2),
            "max_rooms": random.randint(3, 5),
            "city": "New York",
            "neighborhoods": ["Manhattan", "Brooklyn"]
        }
        
        self.client.put(
            "/api/v1/users/preferences/",
            json=preferences,
            name="/api/v1/users/preferences"
        )
    
    # Apartment Tasks
    
    @tag("apartment")
    @task(5)
    def get_apartment_recommendations(self):
        """Get apartment recommendations"""
        self.client.get(
            "/api/v1/apartments/recommendations/",
            name="/api/v1/apartments/recommendations"
        )
    
    @tag("apartment")
    @task(3)
    def get_user_apartments(self):
        """Get user's apartments"""
        self.client.get(
            "/api/v1/apartments/my/",
            name="/api/v1/apartments/my"
        )
    
    @tag("apartment")
    @task(3)
    def get_liked_apartments(self):
        """Get user's liked apartments"""
        self.client.get(
            "/api/v1/apartments/liked/",
            name="/api/v1/apartments/liked"
        )
    
    @tag("apartment")
    @task(2)
    def view_apartment_detail(self):
        """View a specific apartment"""
        if self.apartment_ids:
            apartment_id = random.choice(self.apartment_ids)
            self.client.get(
                f"/api/v1/apartments/{apartment_id}/",
                name="/api/v1/apartments/[id]"
            )
    
    @tag("apartment")
    @task(1)
    def like_apartment(self):
        """Like or unlike an apartment"""
        if self.apartment_ids:
            apartment_id = random.choice(self.apartment_ids)
            like_data = {
                "apartment_id": apartment_id,
                "like": random.choice([True, False])
            }
            
            self.client.post(
                "/api/v1/apartments/preference/",
                json=like_data,
                name="/api/v1/apartments/preference"
            )
    
    # Questionnaire Tasks
    
    @tag("questionnaire")
    @task(1)
    def get_questionnaire(self):
        """Get questionnaire"""
        self.client.get(
            "/api/v1/questionnaire/",
            name="/api/v1/questionnaire"
        )
    
    @tag("questionnaire")
    @task(1)
    def submit_questionnaire_responses(self):
        """Submit questionnaire responses"""
        responses = {
            "responses": [
                {
                    "question_id": "q1",
                    "answer": random.choice(["option1", "option2", "option3"])
                },
                {
                    "question_id": "q2",
                    "answer": random.choice(["option1", "option2", "option3"])
                }
            ]
        }
        
        self.client.post(
            "/api/v1/questionnaire/responses/",
            json=responses,
            name="/api/v1/questionnaire/responses"
        )
