from rest_framework import serializers

from users.models.questionnaire import Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        # fields = ('email', 'password')