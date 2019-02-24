from .models import Question, MCQAnswer, Sitting
import json


def next_question(sitting):
    next_question_id = sitting.question_list.split(',')[0]
    if next_question_id:
        question = Question.objects.get(id=next_question_id)
        return get_question(question)
    else:
        content = {
            'question_id': None,
            'question': None,
            'choices': None
        }
        return content


def get_question(question):
    answers = MCQAnswer.objects.filter(question=question)
    answer_content = []
    for answer in answers:
        answer_content.append({'id': answer.id,
                               'content': answer.content,
                               'correct': answer.correct})
    content = {
        'question_id': question.id,
        'question': question.content,
        'explanation': question.explanation,
        'URL': question.question_url,
        'multiple_answer': multiple_answer(question),
        'choices': answer_content

    }
    return content


def multiple_answer(question):
    answers = MCQAnswer.objects.filter(question=question, correct=True)
    if len(answers)>1:
        return True
    else:
        return False


def get_all_questions(sitting):
    questions_w_answers = sitting.questions_with_user_answers
    final_content = []
    for question, answer in questions_w_answers.items():
        content = get_question(question)
        content['user_answer'] = answer
        final_content.append(content)
    return final_content

