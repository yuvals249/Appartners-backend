# Generated migration for updating about_me field with Hebrew descriptions

from django.db import migrations
import random


def populate_about_me_hebrew(apps, schema_editor):
    """
    Populate the about_me field for all UserDetails with random Hebrew descriptions.
    """
    UserDetails = apps.get_model('users', 'UserDetails')
    
    hebrew_descriptions = [
        "היי! אני סטודנט שנה ב' למדעי המחשב בב״ג. אני בן אדם שקט ונקי, אוהב לבשל, לשחק בערבים ולפעמים סתם לשבת על בירה עם שותפים. מחפש דירה עם אווירה נעימה, שותפים שמכבדים אחד את השני ושומרים על הסדר.",
        
        "סטודנטית לפסיכולוגיה, עובדת חלקית ומבלה הרבה שעות בלימודים. אני מסודרת, אוהבת לשמור על ניקיון ורגועה ברוב הזמן. מאוד חשוב לי יחס טוב ושיח פתוח בבית.",
        
        "אני סטודנט לרפואה, רוב הזמן עסוק בלימודים ובשקט שלי. מאוד חברותי כשיש זמן, אבל מעריך פרטיות וסדר. אשמח לדירה עם שותפים רגועים, שאוהבים בית מסודר.",
        
        "הנדסת תעשייה וניהול שנה שלישית. אוהב לטייל, לשמוע מוזיקה ולבשל בסופי שבוע. לא עושה רעש, נקי, פתוח לתקשורת ורוצה שותפים שאפשר לדבר איתם בקלות.",
        
        "סטודנט להנדסת תוכנה, עובד גם חלקית בתחום. רגוע, מסודר, לא עושה רעש, ומאמין שתקשורת פתוחה עושה את כל ההבדל בבית.",
        
        "לומדת ביולוגיה, אוהבת בעלי חיים, סדר, ואפייה. שותפה שאוהבת בית שקט ונעים, שמכבדת אחרים ושומרת על מרחב אישי.",
        
        "אני סטודנטית לתקשורת, אוהבת לצלם, לראות סרטים ולבשל. שקטה, מסודרת, אוהבת אווירה טובה בבית ומחפשת שותפים בגובה העיניים.",
        
        "לומד היסטוריה ופילוסופיה. קורא הרבה, שומע מוזיקה קלאסית בערבים (בשקט). מעריך שקט, סדר, וכבוד הדדי.",
        
        "סטודנט שנה ב׳ לכלכלה, אוהב סדר, אוהב שותפים שמכבדים ומדברים פתוח. לא עושה מסיבות בבית אבל כן נהנה מערב שותפים קליל.",
        
        "אני סטודנטית לעיצוב, מאוד אוהבת יצירתיות, שקט, סדר ותחושת בית. רוצה לגור עם שותפים שאכפת להם מהאווירה הכללית בדירה.",
        
        "לומדת עבודה סוציאלית, מאוד רגועה ומסודרת. אוהבת לאפות, לתרגל יוגה, ולדבר כשנוח לכולם. שואפת לאווירה מכבדת ונעימה.",
        
        "סטודנט למנהל עסקים, אוהב סדר, מקפיד לשמור על שקט בימים עמוסים, ופתוח לשיחות כשיש זמן. מחפש דירה עם אווירה רגועה.",
        
        "לומד כימיה, שקט בדרך כלל, בעיקר באמצע השבוע. סבלני, נקי, מחפש שותפים קלילים ושומרים על ניקיון בסיסי.",
        
        "סטודנט בינלאומי מצרפת, לומד מדעי המדינה. נקי, חברותי, פתוח, מחפש שותפים שרוצים בית שקט אבל חברי.",
        
        "סטודנט שנה ג׳ למדעי המחשב, רגוע, אוהב סדר, בישול וערבים שקטים. מחפש דירה שבה יש כבוד הדדי ותיאום בסיסי.",
        
        "מהנדס מכונות בשנה ב׳, אוהב להתאמן, לשחק, ולשמור על סדר. זורם אבל גם שומר על מרחב אישי.",
        
        "אני לומדת עיצוב פנים, שקטה ומסודרת. אוהבת לארח חברים מדי פעם, אבל גם מאוד מעריכה זמן לבד.",
        
        "סטודנט לנוירוביולוגיה. משקיע הרבה זמן בלימודים, אבל תמיד פתוח לשיחה טובה. אוהב שקט, סדר ומרחב אישי.",
        
        "אני סטודנט להנדסת תעשייה וניהול, מאוד מסודר, אוהב מוזיקה, בישול ואנשים. חשוב לי לגור עם שותפים שמכבדים אחד את השני.",
        
        "לומדת פסיכולוגיה, עובדת גם חלקית. אוהבת לשמור על דירה נקייה ומסודרת. שואפת לגור עם אנשים תקשורתיים ומכילים."
    ]
    
    # Get all UserDetails objects
    user_details = UserDetails.objects.all()
    
    updated_count = 0
    for user_detail in user_details:
        # Assign a random description to each user
        random_description = random.choice(hebrew_descriptions)
        user_detail.about_me = random_description
        user_detail.save()
        updated_count += 1
    
    print(f"Successfully updated about_me field for {updated_count} users with Hebrew descriptions.")


def reverse_populate_about_me_hebrew(apps, schema_editor):
    """
    Reverse migration - clear all about_me fields.
    """
    UserDetails = apps.get_model('users', 'UserDetails')
    
    # Clear all about_me fields
    UserDetails.objects.all().update(about_me='')
    print("Cleared all about_me fields.")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_populate_about_me2'),
    ]

    operations = [
        migrations.RunPython(
            populate_about_me_hebrew,
            reverse_populate_about_me_hebrew,
        ),
    ]
