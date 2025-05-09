from django.db import migrations


def set_roommates_to_null(apps, schema_editor):
    """
    Set all number_of_roommates values to NULL before the field type change.
    """
    UserPreferences = apps.get_model('users', 'UserPreferences')
    
    # Update all records to set number_of_roommates to NULL
    UserPreferences.objects.all().update(number_of_roommates=None)
    
    # Print a message to confirm the operation
    print("All number_of_roommates values have been set to NULL")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_userpresence'),
    ]

    operations = [
        migrations.RunPython(
            set_roommates_to_null,
            migrations.RunPython.noop  # No reverse migration needed
        ),
    ]
