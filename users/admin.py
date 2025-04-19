from django.contrib import admin
from users.models import UserDetails, UserPreferences, QuestionnaireTemplate, Question, UserResponse, UserPreferencesFeatures
from apartments.models import Feature


class UserPreferencesFeaturesInline(admin.TabularInline):
    model = UserPreferencesFeatures
    extra = 1
    autocomplete_fields = ['feature']


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('first_name', 'last_name', 'phone_number')

    list_display = ('full_name',)

    @admin.display(description='Full Name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('city__name', 'min_price', 'max_price', 'area')

    # Display fields in the admin list view
    list_display = ('user', 'city', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates', 'max_floor', 'area')
    
    # Add filter options
    list_filter = ('city', 'number_of_roommates')
    
    # Add inline for features
    inlines = [UserPreferencesFeaturesInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of empty forms to display
    fields = ('title', 'question_type', 'order', 'weight', 'placeholder', 'options')


@admin.register(QuestionnaireTemplate)
class QuestionnaireTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'question_count')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Number of Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionnaire', 'question_type', 'order', 'weight')
    list_filter = ('questionnaire', 'question_type')
    search_fields = ('title', 'questionnaire__title')
    ordering = ('questionnaire', 'order')


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'response_value', 'created_at')
    list_filter = ('question__questionnaire', 'question')
    search_fields = ('user__email', 'question__title')
    
    def response_value(self, obj):
        return obj.text_response if obj.text_response else obj.numeric_response
    response_value.short_description = 'Response'
