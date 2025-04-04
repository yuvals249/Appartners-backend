from django.db import models
from django.contrib.auth.models import User

class QuestionnaireTemplate(models.Model):
    """Stores the structure of a questionnaire"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)  # Added order field for template ordering
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']  # Default ordering by order field
    
    def __str__(self):
        return self.title

class Question(models.Model):
    """Individual question in a questionnaire"""
    QUESTION_TYPES = (
        ('text', 'Text Input'),
        ('radio', 'Radio Scale'),
    )
    
    id = models.AutoField(primary_key=True)
    questionnaire = models.ForeignKey(QuestionnaireTemplate, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0)
    # For radio options, store as JSON
    options = models.JSONField(null=True, blank=True)
    # For text inputs, store placeholder
    placeholder = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class UserResponse(models.Model):
    """User's answers to questionnaire questions"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questionnaire_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    # Store both text and numeric responses
    text_response = models.TextField(null=True, blank=True)
    numeric_response = models.IntegerField(null=True, blank=True)  # For scale questions (1-5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'question')  # Prevent duplicate answers
        
    def __str__(self):
        return f"{self.user.email} - {self.question.title[:30]}"
