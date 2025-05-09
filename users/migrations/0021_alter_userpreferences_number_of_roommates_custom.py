from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_set_roommates_to_null'),
    ]

    operations = [
        # First, remove the existing column
        migrations.RemoveField(
            model_name='userpreferences',
            name='number_of_roommates',
        ),
        # Then add it back as a JSONField
        migrations.AddField(
            model_name='userpreferences',
            name='number_of_roommates',
            field=models.JSONField(blank=True, default=list, help_text='List of preferred number of roommates', null=True),
        ),
    ]
