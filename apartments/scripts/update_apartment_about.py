#!/usr/bin/env python
"""
Script to update apartment 'about' fields with random sample texts.
Run this script from the project root directory with:
python apartments/scripts/update_apartment_about.py
"""
import os
import sys
import random
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')
django.setup()

from apartments.models.apartment import Apartment

# Sample about texts
ABOUT_SAMPLES = [
    "יחידת דיור מרווחת ומשופצת להשכרה בשכונה ו', מרוהטת קומפלט ובמרחק הליכה מקניון אביה.",
    "דירה נוחה ומרוהטת בלב שכונה ו', כולל מזגן בכל חדר, חשבונות כלולים ונגישות מצוינת לתחבורה ציבורית.",
    "יחידת דיור גדולה בקומה 2 מתוך 4, סמוך למחסני השוק וקניון אביה, עם כניסה מיידית.",
    "דירה עם 2 מזגנים חדשים, דוד שמש וחניה בשפע – מתאימה ליחיד/ה או זוג.",
    "בית מאובזר מלא כולל סלון, מטבח, מוצרי חשמל וריהוט מלא, במיקום מרכזי.",
    "מגורים נוחים במרחק נגיעה מכל השירותים: סופר, קופ\"ח, תחבורה, גני ילדים ועוד.",
    "יחידה פרטית עם מונה חשמל נפרד, מושכרת כולל חשבונות במחיר משתלם במיוחד.",
    "דירה שמורה, נעימה ומרוהטת בקירבת כל המרכזונים של שאול המלך ודרך מצדה.",
    "לוקיישן מרכזי, נגיש ונוח – קרוב לגרנד קניון, קניון אביה ומחסני השוק.",
    "אפשרות לריהוט בסיסי או מלא, עם מחיר גמיש בהתאם – ללא תיווך!",
    "דירה מרוהטת עם שני מזגנים, מרפסת שירות ומיקום מנצח בשכונה ו' החדשה.",
    "יחידת דיור מושקעת להשכרה – קרובה לכל קו תחבורה מרכזי בעיר.",
    "מגורים נוחים עם כל הפינוקים: תמי 4, מכונת כביסה, מקרר, מיקרוגל ועוד.",
    "בית פרטי עם כניסה מיידית, תחזוקה שוטפת, ושכונה שקטה ובטוחה.",
    "דירה עם חדר ממ\"ד, סלון מרווח ושני חדרי שירותים – מושלמת למשפחה קטנה.",
    "20 מטר ממחסני השוק ותחבורה ציבורית לכל יעד בעיר – בלי רכב!",
    "יחידה עם נוף פתוח, חניה זמינה תמיד ואווירה שכונתית נעימה.",
    "שופצה לפני 4 שנים – כוללת דוד שמש חדש וחשמל עצמאי.",
    "קרובה לפארקים, קופות חולים, ומרכזי בילוי – מיקום מנצח.",
    "מחיר שכולל הכל – מים, ארנונה וחשמל עד תקרה – בלי הפתעות."
]

def update_apartment_about_fields():
    """
    Update all apartments with random about text from samples
    """
    # Get all apartments
    apartments = Apartment.objects.all()
    
    # Count of apartments and samples
    apartment_count = apartments.count()
    sample_count = len(ABOUT_SAMPLES)
    
    print(f"Found {apartment_count} apartments and {sample_count} about samples")
    
    # Update counter
    updated_count = 0
    
    # Update each apartment with a random about text
    for apartment in apartments:
        # Select a random about text
        random_about = random.choice(ABOUT_SAMPLES)
        
        # Update the apartment directly in the database to bypass validation
        Apartment.objects.filter(id=apartment.id).update(about=random_about)
        
        updated_count += 1
        
        # Print progress every 10 apartments
        if updated_count % 10 == 0:
            print(f"Updated {updated_count}/{apartment_count} apartments")
    
    print(f"Successfully updated {updated_count} apartments with random about texts")

if __name__ == "__main__":
    print("Starting to update apartment about fields...")
    update_apartment_about_fields()
    print("Done!")
