from .models import Category, SubCategory, Quiz, MCQAnswer, MCQuestion, Sitting
from rest_framework import viewsets
from .serializers import CategorySerializer, SubCategorySerializer, QuizSerializer, MCQAnswerSerializer, \
    MCQuestionSerializer, SittingSerializer
from main.utils import next_question, get_all_questions
from django.core.exceptions import ImproperlyConfigured
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication
from main.permissions import AdminOnly, NormalUserGetOnly
import json
from django.http import HttpResponse, JsonResponse
import matplotlib.pyplot as plt
import base64
from io import BytesIO




class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)

    def get_queryset(self):

        category = self.request.query_params.get('category', None)
        queryset = SubCategory.objects.all()

        if category is not None:
            queryset = queryset.filter(category=category)

        return queryset

    serializer_class = SubCategorySerializer


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)

    def get_queryset(self):
        user = self.request.user
        sub_category = self.request.query_params.get('sub_category', None)
        category = self.request.query_params.get('category', None)
        queryset = Quiz.objects.all()

        if category is not None:
            queryset = queryset.filter(category=category)
        if sub_category is not None:
            queryset = queryset.filter(sub_category=sub_category)
        if user.is_superuser:
            return queryset
        # non admin users cannot see draft quiz
        queryset = queryset.filter(draft=False)
        return queryset

    serializer_class = QuizSerializer


class MCQuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly,)

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        sub_category = self.request.query_params.get('sub_category', None)
        quiz = self.request.query_params.get('quiz', None)
        queryset = MCQuestion.objects.all()

        if category is not None:
            queryset = queryset.filter(category=category)
        if sub_category is not None:
            queryset = queryset.filter(sub_category=sub_category)
        if quiz is not None:
            queryset = queryset.filter(quiz=quiz)
        return queryset
    serializer_class = MCQuestionSerializer


class MCQAnswerViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly,)

    def get_queryset(self):
        queryset = MCQAnswer.objects.all()
        question = self.request.query_params.get('question', None)

        if question is not None:
            queryset = queryset.filter(question=question)

        return queryset

    serializer_class = MCQAnswerSerializer


class SittingViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)

    def get_queryset(self):
        user = self.request.user

        particular_user = self.request.query_params.get('user', None)
        quiz = self.request.query_params.get('quiz', None)

        queryset = Sitting.objects.all()

        if quiz is not None:
            queryset = queryset.filter(quiz=quiz)
        if particular_user is not None:
            queryset = queryset.filter(user=particular_user)
        if user.is_superuser:
            return queryset
        # non admin users can only see their sitting
        queryset = queryset.filter(user=user)
        return queryset

    serializer_class = SittingSerializer


class UserSittingViewSet(APIView):
    """
    quiz id
    """

    authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request, format=None):

        if request.user.is_authenticated():
            quizes=Quiz.objects.all()
            for q in quizes:
                if q.single_attempt is True:
                   a = Sitting.objects.filter(quiz=q.id)
                   a.delete()

            data = request.data
            quiz = Quiz.objects.get(id=data['quiz'])
            try:
                sitting = Sitting.objects.user_sitting(user=request.user, quiz=quiz)
                serializer = SittingSerializer(sitting)
                new_response = serializer.data
                new_response.update(next_question(sitting))
                return Response(data=new_response, status=status.HTTP_200_OK)
            except ImproperlyConfigured:
                return JsonResponse(data={"response" : "no question added for the quiz"}, status=status.HTTP_400_BAD_REQUEST)


class StoreUserAnswerViewSet(APIView):
    """
    sitting id, question id, user_guess id
    """

    authentication_classes = (authentication.TokenAuthentication, )

    def post(self, request, format=None):

        if request.user.is_authenticated():
            data = request.data
            sitting = Sitting.objects.get(id=data['sitting'])
            guess = data['user_guess']

            if request.user == sitting.user:
                question = MCQuestion.objects.get(id=data['question'])
                sitting.add_user_answer(question, guess)
                sitting.remove_question_from_list(question.id)
                prev_answer = []
                if not sitting.quiz.answers_at_end:
                    # correct = question.check_if_correct(guess=guess)
                    # if correct:
                    #     sitting.add_to_score()
                    sitting.calculate_score()
                    prev_answer = question.get_correct_answer()
                    prev_answer[0]['user_guess'] = guess
                serializer = SittingSerializer(sitting)
                new_response = serializer.data
                # new_response.update(next_question(sitting))
                new_response['previous_answer'] = prev_answer

                return JsonResponse(data={"success": "true",
                                          "response": new_response}, status=status.HTTP_200_OK)
        return JsonResponse(data={"success": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class CompleteQuizViewSet(APIView):
    """
    sitting id
    """
    authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request, format=None):

        if request.user.is_authenticated():
            data = request.data
            sitting = Sitting.objects.get(id=data['sitting'])

            if request.user == sitting.user:
                sitting.mark_quiz_complete()
                sitting.calculate_score()

                serializer = SittingSerializer(sitting)
                new_response = serializer.data
                new_response['message'] = sitting.result_message

                return JsonResponse(data={"success": "true",
                                          "response": new_response}, status=status.HTTP_200_OK)
        return JsonResponse(data={"success": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class GetAllQuestionsViewSet(APIView):
    """
    sitting id
    """
    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request, format=None):

        if request.user.is_authenticated():
            sitting = self.request.query_params.get('sitting', None)
            if sitting is not None:
                sitting = Sitting.objects.get(id=sitting)
                quiz = sitting.quiz_id
                title = sitting.quiz.title
                answer_at_end = sitting.quiz.answers_at_end
                number_correct = sitting.number_correct_answer()
                result = sitting.result_message
                totalquestion = len (sitting._question_ids())
                incorrectquestions = totalquestion-number_correct
                pass_marks = sitting.quiz.pass_mark
                points = sitting.quiz.points
                duration_time = sitting.quiz.duration_time
                start_time = sitting.start
                end_time = sitting.end
                timediff = sitting.calculate_time()
                total_unattempt = totalquestion-sitting.no_of_attempt_question()
                single_attempt = sitting.quiz.single_attempt



                if request.user == sitting.user:
                    response = get_all_questions(sitting)

                    return JsonResponse(data={"success": "true",
                                              "response": response,
                                              'quiz': quiz,
                                              'quiz_title': title,
                                              'answer_at_end': answer_at_end,
                                              'result': result,
                                              'number_correct': number_correct,
                                              'incorrect': incorrectquestions,
                                              'totalquestions': totalquestion,
                                              'sitting_id': sitting.id,
                                              'pass_marks': pass_marks,
                                              'points_per_question': points,
                                              'duration_time': duration_time,
                                              'start_time': start_time,
                                              'end_time': end_time,
                                              'time_difference': timediff,
                                              'total_unattempt': total_unattempt,
                                              'single_attempt': single_attempt}, status=status.HTTP_200_OK)
        return JsonResponse(data={"success": "failed"}, status=status.HTTP_400_BAD_REQUEST)



class Records(APIView):

    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request, format=None):

        if request.user.is_authenticated():
            user = self.request.user
            quiz = self.request.query_params.get('quiz', None)
            queryset = Sitting.objects.filter(complete=True)

            if quiz is not None:
                queryset = queryset.filter(quiz=quiz)
            if user.is_superuser:
                param_user = self.request.query_params.get('user', None)
                if param_user is not None:
                    queryset = queryset.filter(user=param_user)
            else:
                queryset = queryset.filter(user=user)

            quizes = queryset.values('quiz').distinct()
            content = []


            for q in quizes:
                no_attempt = 0
                attempt = []
                percent = []
                temp_queryset = queryset.filter(quiz=q['quiz'])
                sittings_content = []
                for sitting in temp_queryset:
                    total_questions = len(sitting._question_ids())
                    number_correct = sitting.number_correct_answer()
                    incorrect = total_questions - number_correct
                    total_unattempt = total_questions - sitting.no_of_attempt_question()
                    percent.append(sitting.get_percent_correct)
                    no_attempt = no_attempt + 1
                    attempt.append(no_attempt)
                    sittings_content.append({'score': sitting.current_score,
                                             'result': sitting.result_message,
                                             'points_per_questions': sitting.quiz.points,
                                             'quiz_pass_marks': sitting.quiz.pass_mark,
                                             'number_correct': number_correct,
                                             'totalquestion': total_questions,
                                             'time_difference': sitting.calculate_time(),
                                             'total_unattempt': total_unattempt,
                                             'percentage': sitting.get_percent_correct,
                                             'incorrect': incorrect,
                                             'start_time': sitting.start,
                                             'stop_time': sitting.end,
                                             'sitting_id': sitting.id})
                print(attempt,percent)
                plt.plot(attempt, percent, 'r-o')
                plt.xlabel('Number of attempts', fontsize=18)
                plt.ylabel('Percentage', fontsize=18)
                figfile = BytesIO()
                plt.savefig(figfile, format='png')
                base = base64.b64encode(figfile.getvalue())
                plt.clf()
                a = str(base)
                image = a.replace(a[:2], '')
                image1 = image.replace(image[len(image)-1], '')
                quiz = temp_queryset[0].quiz
                content.append(({
                    'quiz': q['quiz'],
                    'quiz_title': quiz.title,
                    'single_attempt': quiz.single_attempt,
                    'category': str(quiz.category),
                    'sub_category': str(quiz.sub_category),
                    'graph': image1,
                    'sittings': sittings_content,
                    'attempt': attempt,
                    'percent': percent

                }))

            return JsonResponse(data={'user_id': user.id, "records": content, }, status=status.HTTP_200_OK)

        return JsonResponse(data={"success": "failed"}, status=status.HTTP_400_BAD_REQUEST)