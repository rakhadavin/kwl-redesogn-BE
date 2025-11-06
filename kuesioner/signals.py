from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
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
        
        # Skip polling questions here - they will be handled by m2m_changed signal
        # This prevents the "1 step behind" issue because M2M data isn't saved yet
        if kuesioner.question_type != 'Polling':
            try:
                # Import here to avoid circular import
                from .tasks.polling import send_polling_results_to_teacher
                send_polling_results_to_teacher(str(kuesioner.id), str(question.id))
                print(f"✅ Triggered results update for non-polling question {question.number}")
            except Exception as e:
                print(f"❌ Error sending results: {e}")
        else:
            print(f"⚠️ Skipping post_save for polling question {question.number} - will wait for M2M signal")


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


@receiver(m2m_changed, sender=GuestQuizAnswer.selected_choices.through)
def handle_selected_choices_changed(sender, instance, action, pk_set, **kwargs):
    """
    Handle when selected_choices on GuestQuizAnswer are changed.
    This fixes the timing issue where polling results were sent before M2M data was saved.
    """
    print(f"🔄 M2M signal triggered - Action: {action}, Instance: {instance.id}")
    
    # Only trigger on post_add, post_remove, post_clear (when choices are actually changed and saved)
    if action in ['post_add', 'post_remove', 'post_clear']:
        if instance.question and instance.guest:
            kuesioner = instance.question.kuesioner
            question = instance.question
            
            print(f"📝 M2M change from guest {instance.guest.guest_name} for question {question.number}")
            print(f"🎯 Kuesioner type: {kuesioner.question_type}")
            
            # Only send polling results for polling questions
            if kuesioner.question_type == 'Polling':
                try:
                    print(f"📊 Sending polling results for question {question.number} (M2M change)")
                    # Import here to avoid circular import
                    from .tasks.polling import send_polling_results_to_teacher
                    send_polling_results_to_teacher(str(kuesioner.id), str(question.id))
                    print(f"✅ Triggered polling results update from M2M for question {question.number}")
                except Exception as e:
                    print(f"❌ Error sending polling results from M2M: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️ Skipping polling results - question type is {kuesioner.question_type}")
        else:
            print(f"❌ Missing question or guest in answer instance (M2M)")
    else:
        print(f"⚠️ Ignoring M2M action: {action}")