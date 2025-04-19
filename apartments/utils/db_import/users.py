from datetime import datetime
import random
from .utils import generate_uuid, generate_random_name, generate_random_email, generate_random_phone, generate_random_date

def generate_users(count):
    """
    Generate random users and user details
    
    Args:
        count: Number of users to generate
        
    Returns:
        tuple: (users, user_details)
    """
    users = []
    user_details = []
    
    # Use current timestamp for all records
    now = datetime.now().isoformat()
    
    for _ in range(count):
        user_id = generate_uuid()
        name = generate_random_name()
        email = generate_random_email(name)
        
        # User object
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "is_yad2": True
        }
        
        # User details object
        user_detail = {
            "id": generate_uuid(),
            "user_id": user_id,
            "phone": generate_random_phone(),
            "created_at": now,
            "updated_at": now,
            "is_yad2": True
        }
        
        users.append(user)
        user_details.append(user_detail)
    
    return users, user_details

def generate_user_responses(users):
    """
    Generate random user responses for questions
    
    Args:
        users: List of user objects
        
    Returns:
        list: User responses
    """
    user_responses = []
    
    # Actual question IDs from the database
    question_ids = [
        "1", "2", "3", "4", "5", 
        "6", "7", "8", "9", "10"
    ]
    
    for user in users:
        # Decide how many questions this user will answer (some may skip questions)
        num_questions = random.randint(5, len(question_ids))
        selected_questions = random.sample(question_ids, num_questions)
        
        for question_id in selected_questions:
            # Generate a response between 1-5
            response_value = random.randint(1, 5)
            
            user_response = {
                "id": generate_uuid(),
                "user_id": user["id"],
                "question_id": question_id,
                "response": response_value,
                "created_at": user["created_at"],
                "updated_at": user["updated_at"]
            }
            
            user_responses.append(user_response)
    
    return user_responses
