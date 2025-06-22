# Generated migration to populate about_me field with random descriptions

from django.db import migrations
import random


def populate_about_me(apps, schema_editor):
    """
    Populate the about_me field for all UserDetails with random descriptions
    """
    UserDetails = apps.get_model('users', 'UserDetails')

    about_me_options = [
        "Hey! I'm a second-year computer science student at BGU. I'm clean, quiet during the week, and usually home evenings. I enjoy gaming, cooking, and hanging out when possible. Looking for respectful and chill roommates.",

        "Hi, I study psychology and work part-time in the evenings. I'm very organized and keep common spaces clean. I'm sociable but also like my alone time. I'd love to live with friendly and considerate people.",

        "I'm a first-year medical student, so I'm out most of the day and need a quiet place to study. I'm friendly, very tidy, and love the occasional shared meal or movie night.",

        "Hey! I'm a laid-back person who studies industrial engineering. I like hiking, playing guitar, and having meaningful conversations. Clean and respectful, looking for a calm, open-minded household.",

        "I'm in my final year of software engineering. I enjoy cooking, biking, and keeping a peaceful home environment. I'm clean, responsible, and always happy to help around the house.",

        "I'm a biology student and I love animals, reading, and chill evenings at home. I'm clean, quiet, and enjoy living with people who are respectful and kind.",

        "Hi, I'm studying communications and love photography, music, and spontaneous trips. I keep my space tidy and enjoy living with friendly, easygoing roommates.",

        "Friendly and calm, I'm a first-year student in BGU's humanities faculty. I enjoy reading, painting, and baking. I'm very tidy and looking for a relaxed and respectful apartment vibe.",

        "I'm a clean, respectful engineering student who values a peaceful and organized space. I enjoy running, watching football, and relaxing after class. Not into parties at home.",

        "I'm an architecture student and spend a lot of time working on projects. I'm organized, respectful, and love a quiet, creative environment with roommates who communicate openly.",

        "I study social work and love deep talks, cooking, and yoga. I keep shared spaces clean and believe in mutual respect and honesty among roommates.",

        "Hi! I'm in BGU's business program and also working part-time. I'm organized, friendly, and easy to get along with. Looking for a positive and respectful living situation.",

        "I'm a chemistry student, pretty quiet during the week, and like relaxing or going out a bit on weekends. Clean and respectful, looking for roommates with a similar vibe.",

        "I'm an international student from France studying politics. I'm open-minded, clean, and enjoy both quiet evenings and the occasional get-together.",

        "I'm a second-year student who loves movies, music, and chill weekends. Clean and not dramatic—just want a comfortable, respectful living space.",

        "Hi! I'm studying mechanical engineering. I enjoy gaming, working out, and cooking. I keep common areas clean and value open communication with roommates.",

        "I'm a design student who loves creating things and keeping things tidy. I'm calm, open to conversation, and would like roommates who care about the home environment.",

        "BGU student in neuroscience. I like my space, study a lot, but I'm always down for a short chat or dinner together. I keep the apartment quiet and clean.",

        "I'm in my third year, studying economics. I'm social but appreciate quiet during the week. I cook, keep shared spaces neat, and am easy to live with.",

        "Hi, I study computer science and work part-time in tech. I'm clean, relaxed, and appreciate direct and respectful communication. Looking for a cozy place with good vibes."
    ]

    # Get all UserDetails
    user_details = UserDetails.objects.all()

    # Update each user with a random about_me description
    for user_detail in user_details:
        user_detail.about_me = random.choice(about_me_options)
        user_detail.save()

    print(f"Updated {user_details.count()} user profiles with random about_me descriptions")


def reverse_populate_about_me(apps, schema_editor):
    """
    Reverse migration - clear the about_me field for all users
    """
    UserDetails = apps.get_model('users', 'UserDetails')
    UserDetails.objects.all().update(about_me=None)
    print("Cleared all about_me descriptions")


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0026_populate_about_me'),
    ]

    operations = [
        migrations.RunPython(populate_about_me, reverse_populate_about_me),
    ]
