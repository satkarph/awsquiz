from django.contrib import admin
from authemail.admin import EmailUserAdmin
from django.contrib.auth import get_user_model

from .models import Quiz, Question, Category, SubCategory, MCQAnswer, MCQuestion, Sitting


class QuizUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                       'is_superuser', 'is_verified',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom info', {'fields': ('date_of_birth',)}),
    )


class AnswerInline(admin.TabularInline):
    model = MCQAnswer


class QuizAdmin(admin.ModelAdmin):

    list_display = ('title', 'category', )
    list_filter = ('category',)
    search_fields = ('description', 'category', )


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category', )


class SubCategoryAdmin(admin.ModelAdmin):
    search_fields = ('sub_category', )
    list_display = ('sub_category', 'category',)
    list_filter = ('category',)


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'sub_category',
              'figure', 'quiz', 'explanation', 'answer_order', 'question_url')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class MCQAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'content', 'correct')
    # search_fields=('question','quiz')
    list_filter = ('question',)

    # filter_horizontal = ('question',)

class SittingAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz')
    list_filter = ('quiz',)

admin.site.register(get_user_model(), QuizUserAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(MCQAnswer,MCQAnswerAdmin)
admin.site.register(Sitting,SittingAdmin)