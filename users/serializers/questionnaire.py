from rest_framework import serializers
from users.models.questionnaire import QuestionnaireTemplate, Question, UserResponse

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'question_type', 'options', 'placeholder', 'order']

class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionnaireTemplate
        fields = ['id', 'title', 'description', 'questions']
    
    def get_questions(self, obj):
        # Get questions ordered by the 'order' field
        questions = obj.questions.all().order_by('order')
        return QuestionSerializer(questions, many=True).data

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['question', 'text_response', 'numeric_response']
    
    def validate(self, data):
        """Validate that the response matches the question type"""
        question = data['question']
        if question.question_type == 'text' and not data.get('text_response'):
            raise serializers.ValidationError("Text response required for this question type")
        elif question.question_type == 'radio' and data.get('numeric_response') is None:
            raise serializers.ValidationError("Numeric response required for this question type")
        return data

class UserResponseBulkSerializer(serializers.Serializer):
    """Serializer for submitting multiple responses at once"""
    responses = UserResponseSerializer(many=True)
    
    def create(self, validated_data):
        # Get user from context (must be provided by the view)
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User not provided in context")
            
        responses_data = validated_data.pop('responses')
        responses = []
        
        for response_data in responses_data:
            # Check if response already exists and update it
            response, created = UserResponse.objects.update_or_create(
                user=user,
                question=response_data['question'],
                defaults={
                    'text_response': response_data.get('text_response'),
                    'numeric_response': response_data.get('numeric_response')
                }
            )
            responses.append(response)
        
        return {'responses': responses}