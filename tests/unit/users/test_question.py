import pytest
from users.models import Question
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_question_str_representation(test_questionnaire_template):
    question = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Test Question',
        question_type='text',
        order=1
    )
    assert str(question) == 'Test Question'

@pytest.mark.django_db
def test_question_ordering(test_questionnaire_template):
    # Create questions in reverse order
    question2 = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Question 2',
        question_type='text',
        order=2
    )
    question1 = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Question 1',
        question_type='text',
        order=1
    )
    
    # Get all questions
    questions = Question.objects.all()
    
    # Check ordering
    assert list(questions) == [question1, question2]

@pytest.mark.django_db
def test_question_cascade_delete_template(test_questionnaire_template):
    # Create a question
    question = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Test Question',
        question_type='text',
        order=1
    )
    
    # Delete the template
    test_questionnaire_template.delete()
    
    # The question should be deleted
    assert not Question.objects.filter(id=question.id).exists()

@pytest.mark.django_db
def test_question_question_type_choices(test_questionnaire_template):
    with pytest.raises(ValidationError):
        question = Question(
            questionnaire=test_questionnaire_template,
            title='Test Question',
            question_type='invalid_type',
            order=1
        )
        question.full_clean()
        question.save() 