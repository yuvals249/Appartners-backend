import uuid
import random
import string
from datetime import datetime, timedelta

def generate_uuid():
    """Generate a random UUID"""
    return str(uuid.uuid4())

def generate_random_name():
    """Generate a random name"""
    first_names = [
        "Adam", "Alex", "Aaron", "Ben", "Carl", "Dan", "David", "Edward", "Fred", "Frank",
        "George", "Hal", "Hank", "Ike", "John", "Jack", "Joe", "Larry", "Monte", "Matthew",
        "Mark", "Nathan", "Otto", "Paul", "Peter", "Roger", "Roger", "Steve", "Thomas", "Tim",
        "Ty", "Victor", "Walter", "Noa", "Tamar", "Yael", "Maya", "Shira", "Talia", "Michal",
        "Avigail", "Ayala", "Hila", "Roni", "Lihi", "Yuval", "Amit", "Shani", "Adi", "Gal"
    ]
    
    last_names = [
        "Anderson", "Ashwoon", "Aikin", "Bateman", "Bongard", "Bowers", "Boyd", "Cannon", "Cast",
        "Deitz", "Dewalt", "Ebner", "Frick", "Hancock", "Haworth", "Hesch", "Hoffman", "Kassing",
        "Knutson", "Lawless", "Lawicki", "Mccord", "McCormack", "Miller", "Myers", "Nugent",
        "Ortiz", "Orwig", "Ory", "Paiser", "Pak", "Pettigrew", "Quinn", "Quizoz", "Ramachandran",
        "Resnick", "Sagar", "Schickowski", "Schiebel", "Sellon", "Severson", "Shaffer", "Solberg",
        "Soloman", "Sonderling", "Soukup", "Soulis", "Stahl", "Sweeney", "Tandy", "Trebil", "Trusela",
        "Trussel", "Turco", "Uddin", "Uflan", "Ulrich", "Upson", "Vader", "Vail", "Valente", "Van Zandt",
        "Vanderpoel", "Ventotla", "Vogal", "Wagle", "Wagner", "Wakefield", "Weinstein", "Weiss", "Woo",
        "Yang", "Yates", "Yocum", "Zeaser", "Zeller", "Ziegler", "Bauer", "Baxster", "Casal", "Cataldi",
        "Cohen", "Levy", "Israeli", "Rosenberg", "Friedman", "Goldberg", "Schwartz", "Katz", "Mizrachi"
    ]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name):
    """Generate a random email based on name"""
    name_parts = name.lower().split()
    email_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "mail.com"]
    
    # Create email with name parts and random number
    random_num = random.randint(1, 999)
    email = f"{name_parts[0]}.{name_parts[-1]}{random_num}@{random.choice(email_providers)}"
    return email

def generate_random_phone():
    """Generate a random Israeli phone number"""
    prefixes = ["050", "052", "053", "054", "055", "058"]
    suffix = ''.join(random.choices(string.digits, k=7))
    return f"{random.choice(prefixes)}{suffix}"

def generate_random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)
