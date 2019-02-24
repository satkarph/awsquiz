"""quiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.views import CategoryViewSet, SubCategoryViewSet, QuizViewSet, MCQAnswerViewSet, MCQuestionViewSet, \
    SittingViewSet, UserSittingViewSet, StoreUserAnswerViewSet, CompleteQuizViewSet, GetAllQuestionsViewSet,Records


router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet, 'Category')
router.register(r'subcategory', SubCategoryViewSet, 'SubCategory')
router.register(r'quiz', QuizViewSet, 'Quiz')
router.register(r'mcqanswer', MCQAnswerViewSet, 'MCQAnswer')
router.register(r'mcquestion', MCQuestionViewSet, 'MCQuestion')
router.register(r'sitting', SittingViewSet, 'Sitting')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api/accounts/', include('authemail.urls')),
    url(r'usersitting', UserSittingViewSet.as_view()),
    url(r'store_answer', StoreUserAnswerViewSet.as_view()),
    url(r'complete_quiz', CompleteQuizViewSet.as_view()),
    url(r'all_questions', GetAllQuestionsViewSet.as_view()),
    url(r'records', Records.as_view())
]