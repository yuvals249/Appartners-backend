from django.db import models

class Questionnaire(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    title = models.TextField(null=True)
