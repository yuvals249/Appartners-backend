import pytest
from users.models import QuestionnaireTemplate


def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_questionnaire_template_str_representation(test_questionnaire_template):
    assert str(test_questionnaire_template) == test_questionnaire_template.title

@pytest.mark.django_db
def test_questionnaire_template_ordering():
    # Create templates with different order values
    template1 = QuestionnaireTemplate.objects.create(
        title='Template 1',
        description='First template',
        order=2
    )
    template2 = QuestionnaireTemplate.objects.create(
        title='Template 2',
        description='Second template',
        order=1
    )
    
    # Get all templates ordered by order field
    templates = QuestionnaireTemplate.objects.all()
    
    # Check that templates are ordered correctly
    assert templates[0] == template2  # order=1
    assert templates[1] == template1  # order=2

@pytest.mark.django_db
def test_questionnaire_template_auto_timestamps(test_questionnaire_template):
    assert test_questionnaire_template.created_at is not None
    assert test_questionnaire_template.updated_at is not None
    assert_timestamps_equal(test_questionnaire_template.created_at, test_questionnaire_template.updated_at)

@pytest.mark.django_db
def test_questionnaire_template_update_timestamp(test_questionnaire_template):
    initial_updated_at = test_questionnaire_template.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the template
    test_questionnaire_template.title = 'Updated Template'
    test_questionnaire_template.save()
    
    # Check that updated_at was updated
    test_questionnaire_template.refresh_from_db()
    assert test_questionnaire_template.updated_at > initial_updated_at 