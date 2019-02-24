from django.db import models
from authemail.models import EmailAbstractUser, EmailUserManager
import re
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.conf import settings
from model_utils.managers import InheritanceManager
import json


# Create your models here.
class QuizUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField('Date of birth', null=True,
        blank=True)

    objects = EmailUserManager()


class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category)
                                   .lower())

        new_category.save()
        return new_category


class Category(models.Model):

    category = models.CharField(
        verbose_name=_("Category"),
        max_length=250, blank=True,
        unique=True, null=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.category


class SubCategory(models.Model):

    sub_category = models.CharField(
        verbose_name=_("Sub-Category"),
        max_length=250, blank=True, null=True)

    category = models.ForeignKey(
        Category, null=True, blank=True,
        verbose_name=_("Category"))

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Sub-Category")
        verbose_name_plural = _("Sub-Categories")

    def __str__(self):
        return self.sub_category + " (" + self.category.category + ")"

    @property
    def category_name(self):
        return self.category.category


class Quiz(models.Model):


    title = models.CharField(
        verbose_name=_("Title"),
        max_length=600, blank=False)

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True, help_text=_("a description of the quiz"))

    category = models.ForeignKey(
        Category, null=True, blank=True,
        verbose_name=_("Category"))

    sub_category = models.ForeignKey(
        SubCategory, null=True, blank=True,
        verbose_name=_("Sub-Category"))

    random_order = models.BooleanField(
        blank=False, default=False,
        verbose_name=_("Random Order"),
        help_text=_("Display the questions in "
                    "a random order or as they "
                    "are set?"))

    max_questions = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("Max Questions"),
        help_text=_("Number of questions to be answered on each attempt."))

    answers_at_end = models.BooleanField(
        blank=False, default=False,
        help_text=_("Correct answer is NOT shown after question."
                    " Answers displayed at the end."),
        verbose_name=_("Answers at end"))

    exam_paper = models.BooleanField(
        blank=False, default=False,
        help_text=_("If yes, the result of each"
                    " attempt by a user will be"
                    " stored. Necessary for marking."),
        verbose_name=_("Exam Paper"))

    single_attempt = models.BooleanField(
        blank=False, default=False,
        help_text=_("If yes, only one attempt by"
                    " a user will be permitted."
                    " Non users cannot sit this exam."),
        verbose_name=_("Single Attempt"))

    points = models.IntegerField(
        blank=True, default=1,
        verbose_name=_("Points"),
        help_text=_("Points per question."))

    pass_mark = models.SmallIntegerField(
        blank=True, default=0,
        verbose_name=_("Pass Mark"),
        help_text=_("Percentage required to pass exam."),
        validators=[MaxValueValidator(100)])

    success_text = models.TextField(
        blank=True, help_text=_("Displayed if user passes."),
        verbose_name=_("Success Text"))

    fail_text = models.TextField(
        verbose_name=_("Fail Text"),
        blank=True, help_text=_("Displayed if user fails."))

    draft = models.BooleanField(
        blank=True, default=False,
        verbose_name=_("Draft"),
        help_text=_("If yes, the quiz is not displayed"
                    " in the quiz list and can only be"
                    " taken by users who can edit"
                    " quizzes."))
    duration_time = models.TimeField(_(u"Conversation Time"), blank=True, default= None, null=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        if self.single_attempt is True:
            self.answers_at_end = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)



    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")

    def __str__(self):
        return self.title

    @property
    def has_questions(self):
        return MCQuestion.objects.filter(quiz=self).exists()

    @property
    def category_name(self):
        return self.category.category

    @property
    def sub_category_name(self):
        return self.sub_category.sub_category

class Question(models.Model):
    """
    Base class for all question types.
    Shared properties placed here.
    """

    quiz = models.ManyToManyField(Quiz,
                                  verbose_name=_("Quiz"),
                                  blank=True)

    category = models.ForeignKey(Category,
                                 verbose_name=_("Category"),
                                 blank=True,
                                 null=True)

    sub_category = models.ForeignKey(SubCategory,
                                     verbose_name=_("Sub-Category"),
                                     blank=True,
                                     null=True)

    figure = models.ImageField(upload_to='uploads/%Y/%m/%d',
                               blank=True,
                               null=True,
                               verbose_name=_("Figure"))

    content = models.CharField(max_length=10000,
                               blank=False,
                               help_text=_("Enter the question text that "
                                           "you want displayed"),
                               verbose_name=_('Question'))

    explanation = models.TextField(max_length=20000,
                                   blank=True,
                                   help_text=_("Explanation to be shown "
                                               "after the question has "
                                               "been answered."),
                                   verbose_name=_('Explanation'))

    question_url = models.TextField(max_length=500,
                                    default=None,
                                    null=True, blank=True,
                                    verbose_name=_('URL-Answer'))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['category']

    def __str__(self):
        return self.content


ANSWER_ORDER_OPTIONS = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)


class MCQuestion(Question):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which multichoice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")

    def check_if_correct(self, guess):
        guess = eval(guess)
        if type(guess) == int:
            guess = [guess]
        for g in guess:
            answer = MCQAnswer.objects.get(id=g)
            if answer.correct is False:
                return False
        correct_answers = MCQAnswer.objects.filter(question=self, correct=True)
        if len(correct_answers) == len(guess):
            return True
        return False

    def get_correct_answer(self):
        answers = MCQAnswer.objects.filter(question=self, correct=True)
        answer_content = []
        for answer in answers:
            answer_content.append({'id': answer.id,
                                   'content': answer.content,
                                   'explanation': self.explanation})
        return answer_content

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(MCQAnswer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(MCQAnswer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return MCQAnswer.objects.get(id=guess).content


class MCQAnswer(models.Model):
    question = models.ForeignKey(MCQuestion, verbose_name=_("Question"), on_delete=models.CASCADE)
    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Enter the answer text that "
                                           "you want displayed"),
                               verbose_name=_("Content"))

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Is this a correct answer?"),
                                  verbose_name=_("Correct"))

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")


class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = Question.objects.filter(quiz=quiz) \
                                            .order_by('?')
        else:
            question_set = Question.objects.filter(quiz=quiz)
        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. '
                                       'Please configure questions properly')

        if quiz.max_questions and quiz.max_questions < len(question_set):
            question_set = question_set[:quiz.max_questions]

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True and self.filter(user=user,
                                                       quiz=quiz,
                                                       complete=True)\
                                               .exists():
            return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        return sitting


class Sitting(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))

    quiz = models.ForeignKey(Quiz, verbose_name=_("Quiz"))

    question_order = models.CommaSeparatedIntegerField(
        max_length=1024, verbose_name=_("Question Order"))

    question_list = models.CommaSeparatedIntegerField(
        max_length=1024, verbose_name=_("Question List"))

    current_score = models.IntegerField(verbose_name=_("Current Score"))

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name=_("Complete"))

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name=_("User Answers"))

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name=_("Start"))

    end = models.DateTimeField(null=True, blank=True, verbose_name=_("End"))

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", _("Can see completed exams.")),)

    # def get_first_question(self):
    #     """
    #     Returns the next question.
    #     If no question is found, returns False
    #     Does NOT remove the question from the front of the list.
    #     """
    #     if not self.question_list:
    #         return False
    #
    #     first, _ = self.question_list.split(',', 1)
    #     question_id = int(first)
    #     return Question.objects.get(id=question_id)
    #
    # def remove_first_question(self):
    #     if not self.question_list:
    #         return
    #
    #     _, others = self.question_list.split(',', 1)
    #     self.question_list = others
    #     self.save()

    def remove_question_from_list(self, question_id):
        """
        Remove the provided question_id form question_list
        :param question_id:
        :return:
        """
        if not self.question_list:
            return False
        question_ids = self.question_list.split(',')
        try:
            question_ids.remove(str(question_id))
        except ValueError:
            pass
        self.question_list = ",".join(question_ids)
        self.save()

    def add_to_score(self):
        points = self.quiz.points
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        points = self.quiz.points
        divisor = len(self._question_ids())*points
        if divisor < 1:
            return 0  # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = float((dividend / divisor) * 100)

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.quiz.success_text
        else:
            return self.quiz.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        try:
            current[str(question.id)] = guess
        except KeyError:
            current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.quiz.question_set.filter(id__in=question_ids),
            key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                try:
                    question.user_answer = user_answers[str(question.id)]
                except KeyError:
                    question.user_answer = None
        return questions

    def calculate_score(self):
        user_answers = json.loads(self.user_answers)
        points = self.quiz.points
        score = 0
        for key, value in user_answers.items():
            question = MCQuestion.objects.get(id=key)
            correct = question.check_if_correct(value)
            if correct:
                score += points
        self.current_score = score
        self.save()

    def number_correct_answer(self):
        user_answers = json.loads(self.user_answers)
        score = 0
        for key, value in user_answers.items():
            question = MCQuestion.objects.get(id=key)
            correct = question.check_if_correct(value)
            if correct:
                score = score + 1
        return score

    def no_of_attempt_question(self):
        user_answers = json.loads(self.user_answers)
        return len(user_answers)

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    def progress(self):
        """
        Returns the number of questions answered so far and the total number of
        questions.
        """
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total

    def calculate_time(self):

        if self.end == None:
            return None

        time_diff = self.end-self.start
        secs = time_diff.total_seconds()
        days = secs//86400
        hours = int((secs - days*86400)//3600)
        minutes = int((secs - days*86400 - hours*3600)//60)
        seconds = int(secs - days*86400 - hours*3600 - minutes*60)
        result = ("{}:".format(hours)) + \
             ("{}:".format(minutes)) + \
             ("{}".format(seconds))
        return result
    


