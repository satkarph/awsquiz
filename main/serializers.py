from rest_framework import serializers
from .models import MCQuestion, MCQAnswer, SubCategory, Category, Quiz, Sitting


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'category',
        )


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = (
            'id',
            'category',
            'sub_category',
            'category_name',
        )


class QuizSerializer(serializers.ModelSerializer):
    has_questions = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'category',
            'sub_category',
            'random_order',
            'max_questions',
            'answers_at_end',
            'exam_paper',
            'single_attempt',
            'pass_mark',
            'success_text',
            'fail_text',
            'draft',
            'points',
            'has_questions',
            'duration_time',
            'category_name',
            'sub_category_name',
        )


class MCQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MCQuestion
        fields = (
            'id',
            'quiz',
            'category',
            'sub_category',
            'figure',
            'content',
            'explanation',
            'answer_order',
            'question_url',
        )


class MCQAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = MCQAnswer
        fields = (
            'id',
            'question',
            'content',
            'correct',
        )


class SittingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sitting
        fields = (
            'id',
            'user',
            'quiz',
            'question_order',
            'question_list',
            'current_score',
            'complete',
            'user_answers',
            'start',
            'end'
        )
