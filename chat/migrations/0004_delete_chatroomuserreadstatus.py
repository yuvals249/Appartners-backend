# Generated by Django 4.2.17 on 2025-05-02 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_message_is_read_message_read_at_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChatRoomUserReadStatus',
        ),
    ]
