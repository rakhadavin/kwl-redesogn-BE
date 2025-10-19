import time
from celery import shared_task
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Quiz, Question, Choice

@shared_task(bind=True)
def start_quiz_sequence(self, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(
            quiz=quiz
        ).prefetch_related('choices').order_by('created_at')

        channel_layer = get_channel_layer()
        room_group_name = f'quiz_{quiz_id}'
        room_group_name_teacher = f'quiz_{quiz_id}_teacher'
        total_questions = questions.count()

        for index, question in enumerate(questions, start=1):
            question_number = index
            choices_data = [
                {
                    'id': str(choice.id),
                    'choice_text': choice.choice_text,
                }
                for choice in question.choices.all()
            ]

            async_to_sync(channel_layer.group_send)(
                room_group_name_teacher,
                {
                    'type': 'question_start',
                    'question_number': question_number,
                    'total_questions': total_questions,
                    'question': {
                        'id': str(question.id),
                        'question_text': question.question_text,
                        'score': question.score,
                        'choices': choices_data,
                    },
                    # 'duration': question.time_limit,
                    'duration': 30,
                }
            )
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'question_start',
                    'question_number': question_number,
                    'total_questions': total_questions,
                    'question': {
                        'id': str(question.id),
                        'question_text': question.question_text,
                        'score': question.score,
                        'choices': choices_data,
                    },
                    # 'duration': question.time_limit,
                    'duration': 30,
                }
            )
            # duration = question.time_limit if hasattr(question, 'time_limit') else 30
            duration = 30 
            time.sleep(duration)

            correct_choices = list(
                question.choices.filter(is_correct=True).values_list('id', flat=True)
            )

            async_to_sync(channel_layer.group_send)(
                room_group_name_teacher,
                {
                    'type': 'question_end',
                    'question_id': str(question.id),
                    'question_number': question_number,
                    'correct_choice_ids': [str(choice_id) for choice_id in correct_choices],
                }
            )
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'question_end',
                    'question_id': str(question.id),
                    'question_number': question_number,
                    'correct_choice_ids': [str(choice_id) for choice_id in correct_choices],
                }
            )

            if question_number < total_questions:
                time.sleep(3)

        quiz.if_finished = True
        quiz.save()


    except Quiz.DoesNotExist:
        error_msg = f"Quiz {quiz_id} not found"
        print(f"❌ {error_msg}")
        return error_msg
        
    except Exception as e:
        error_msg = f"Error in quiz {quiz_id}: {str(e)}"
        print(f"❌ {error_msg}")
        raise self.retry(exc=e, countdown=5, max_retries=3)