from django.db.models.signals import post_save, post_delete, pre_save
from .models import Kuesioner, GuestQuizAttempt, KuesionerSession, GuestQuizAnswer
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# from .tasks import start_kuesioner_sequence

channel_layer = get_channel_layer()
_kuesioner_original_state = {}

@receiver(post_save, sender=GuestQuizAttempt)
def handle_participant_joined(sender, instance, created, **kwargs):
    if created:
        kuesioner_id = str(instance.kuesioner.id)
        if instance.session:
            session = instance.session
            session.total_participants = session.attempts.count()
            session.save()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'kuesioner_{kuesioner_id}_teacher',  
                {'type': 'participant'}
            )


@receiver(post_delete, sender=GuestQuizAttempt)
def handle_participant_left(sender, instance, **kwargs):
    kuesioner_id = str(instance.kuesioner.id)
    if instance.session:
        try:
            session = KuesionerSession.objects.get(id=instance.session.id)
            session.total_participants = max(0, session.attempts.count())
            session.save()
        except KuesionerSession.DoesNotExist:
            print(f"⚠️ Session {instance.session.id} no longer exists")
    
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'kuesioner_{kuesioner_id}_teacher',  
            {'type': 'participant'}
        )


@receiver(post_save, sender=GuestQuizAnswer)
def handle_answer_submitted(sender, instance, created, **kwargs):
    """Handle when a guest submits or updates an answer"""
    if instance.question and instance.guest:
        kuesioner = instance.question.kuesioner
        question = instance.question
        
        # Only send polling results for polling questions
        if kuesioner.question_type == 'Polling':
            try:
                # Import here to avoid circular import
                from .tasks.polling import send_polling_results_to_teacher
                send_polling_results_to_teacher(str(kuesioner.id), str(question.id))
                print(f"✅ Triggered polling results update for question {question.number}")
            except Exception as e:
                print(f"❌ Error sending polling results: {e}")


@receiver(post_delete, sender=GuestQuizAnswer)
def handle_answer_deleted(sender, instance, **kwargs):
    """Handle when a guest answer is deleted"""
    if instance.question and instance.guest:
        kuesioner = instance.question.kuesioner
        question = instance.question
        
        # Only send polling results for polling questions
        if kuesioner.question_type == 'Polling':
            try:
                # Import here to avoid circular import
                from .tasks.polling import send_polling_results_to_teacher
                send_polling_results_to_teacher(str(kuesioner.id), str(question.id))
                print(f"✅ Triggered polling results update after deletion for question {question.number}")
            except Exception as e:
                print(f"❌ Error sending polling results after deletion: {e}")