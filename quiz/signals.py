from django.db.models.signals import post_save, post_delete, pre_save
from channels.layers import get_channel_layer
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import GuestQuizAttempt, Quiz
from threading import Timer
# from .tasks import start_quiz_sequence

channel_layer = get_channel_layer()

_update_timers = {}
_quiz_original_state = {}

def send_participants_update(quiz_id):
    """Send participants update dengan delay untuk debouncing"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        all_guests = GuestQuizAttempt.objects.filter(
            quiz=quiz, 
            completed_at__isnull=True,
            guest_name__isnull=False
        )

        participants_data = [
            {
                'id': str(guest.id),
                'guest_name': guest.guest_name,
                'joined_at': guest.created_at.isoformat()
            }
            for guest in all_guests
        ]

        quiz_status = {
            'is_started': quiz.is_started,
            'if_finished': quiz.if_finished,
            'is_lobby': quiz.is_lobby,
        }

        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'quiz_{quiz.id}',  
                {
                    'type': 'participant',
                    'participants': participants_data,
                    'quiz_status': quiz_status,
                    'total_participants': len(participants_data)
                }
            )

    except Quiz.DoesNotExist:
        print(f"⚠️ Quiz {quiz_id} not found")
        pass
    finally:
        if quiz_id in _update_timers:
            del _update_timers[quiz_id]

@receiver(post_save, sender=GuestQuizAttempt)
def handle_participant_joined(sender, instance, **kwargs):
    quiz_id = str(instance.quiz.id)
    if quiz_id in _update_timers:
        _update_timers[quiz_id].cancel()
    
    timer = Timer(0.5, send_participants_update, [quiz_id])
    _update_timers[quiz_id] = timer
    timer.start()

@receiver(post_delete, sender=GuestQuizAttempt)
def handle_participant_left(sender, instance, **kwargs):
    quiz_id = str(instance.quiz.id)
    if quiz_id in _update_timers:
        _update_timers[quiz_id].cancel()
    
    timer = Timer(0.5, send_participants_update, [quiz_id])
    _update_timers[quiz_id] = timer
    timer.start()

@receiver(pre_save, sender=Quiz)
def capture_quiz_original_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Quiz.objects.get(pk=instance.pk)
            _quiz_original_state[instance.pk] = {
                'is_started': original.is_started,
                'is_lobby': original.is_lobby,
                'if_finished': original.if_finished,
            }
        except Quiz.DoesNotExist:
            pass
        
@receiver(post_save, sender=Quiz)
def handle_quiz_state_changes(sender, instance, created, **kwargs):
    quiz_id = str(instance.id)
    original_state = _quiz_original_state.get(instance.pk, {})
    was_started = original_state.get('is_started', False)
    was_finished = original_state.get('if_finished', False)
    if instance.is_started and not was_started:
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'quiz_{instance.id}',
                {
                    'type': 'quiz_started',
                    'quiz_id': quiz_id,
                    'message': 'Quiz telah dimulai!',
                    'quiz_status': {
                        'is_started': True,
                        'is_lobby': False,
                        'if_finished': False,
                    }
                }
            )
            # start_quiz_sequence.delay(quiz_id)

    if instance.if_finished and not was_finished:
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'quiz_{instance.id}',
                {
                    'type': 'quiz_finished',
                    'quiz_id': quiz_id,
                    'message': 'Quiz telah selesai!',
                    'quiz_status': {
                        'is_started': False,
                        'is_lobby': False,
                        'if_finished': True,
                    }
                }
            )

    if instance.pk in _quiz_original_state:
        del _quiz_original_state[instance.pk]


