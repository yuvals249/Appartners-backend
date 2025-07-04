# Generated by Django 4.2.17 on 2025-03-31 20:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apartments', '0008_apartmentuserlike'),
        ('users', '0004_alter_userpreferences_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.TextField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userpreferences',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_user_preferences', to='apartments.city'),
        ),
        migrations.AlterField(
            model_name='userpreferences',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_user_preferences', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='UserPreferencesFeatures',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feature_user_preferences', to='apartments.feature')),
                ('user_preferences', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_preference_features', to='users.userpreferences')),
            ],
        ),
    ]
