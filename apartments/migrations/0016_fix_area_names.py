from django.db import migrations

def remove_trailing_apostrophe(apps, schema_editor):
    """
    Remove trailing apostrophe from area names in the Apartment model.
    """
    Apartment = apps.get_model('apartments', 'Apartment')
    
    # Areas that need fixing (those with trailing apostrophe)
    areas_to_fix = {
        "שכונה ט'": "שכונה ט",
        "שכונה ו'": "שכונה ו",
        "שכונה ה'": "שכונה ה",
        "שכונה ד'": "שכונה ד",
        "שכונה ג'": "שכונה ג",
        "שכונה ב'": "שכונה ב",
        "שכונה א'": "שכונה א",
    }
    
    # Update each area name
    for old_area, new_area in areas_to_fix.items():
        Apartment.objects.filter(area=old_area).update(area=new_area)

class Migration(migrations.Migration):

    dependencies = [
        ('apartments', '0015_fix_yad2_apartment_area'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(remove_trailing_apostrophe),
    ]
